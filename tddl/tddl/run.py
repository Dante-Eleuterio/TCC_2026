# BSD 2-Clause License
#
# Copyright (c) 2026, Dante Eĺeutério dos Santos
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import re
import signal
import subprocess
from pathlib import Path
from .helpers import die, info
import shutil


# Thresholds padrão para --lizard.
DEFAULT_LIZARD_CCN    = 10
DEFAULT_LIZARD_LENGTH = 50
DEFAULT_LIZARD_ARGS   = 5


def _resolve_executable(build_dir: Path, target: str) -> Path:
    executable = build_dir / target
    if not executable.exists():
        candidates = list(build_dir.rglob(target))
        if not candidates:
            die(f"Test executable not found after build: {target}")
        executable = candidates[0]
    return executable


# ----------------------------------------------------------------------------
#  Detecção de crash por sinal (SIGSEGV, SIGABRT, SIGBUS, ...)
# ----------------------------------------------------------------------------
#
# Quando o binário de teste morre por sinal, Python/subprocess relata o
# exit code de duas formas dependendo de quem matou o processo:
#
#   * Diretamente pelo kernel:    returncode = -N    (ex: -11 para SIGSEGV)
#   * Encerrado pelo shell/init:  returncode = 128+N (ex: 139 para SIGSEGV)
#
# Detectamos ambos para robustez. Quando rodando sob valgrind, o exit code
# pode vir normalizado pela --error-exitcode=1 — nesse caso, o sinal é
# mascarado e cai no fluxo normal de FAIL. Não tem como recuperar isso
# aqui; o valgrind imprime a info no stderr e o tddl já mostra.
# ----------------------------------------------------------------------------

def _signal_from_returncode(returncode: int) -> int | None:
   
    if returncode < 0:
        return -returncode
    if returncode > 128:
        return returncode - 128
    return None


def _signal_name(signum: int) -> str:
    
    try:
        return signal.Signals(signum).name
    except (ValueError, AttributeError):
        return f"signal {signum}"


# Regex para capturar a última linha de teste que o Unity conseguiu
# imprimir antes de morrer. Funciona com ou sem mensagem, em qualquer
# das três status finais.
_UNITY_RESULT_LINE = re.compile(
    r'^[^:\n]+:(\d+):([^:\n]+):(PASS|FAIL|IGNORE)',
    re.MULTILINE,
)


def _last_test_before_crash(captured_stdout: str) -> tuple[str, int] | None:
   
    text = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', captured_stdout)
    matches = _UNITY_RESULT_LINE.findall(text)
    if not matches:
        return None
    last_line, last_name, _status = matches[-1]
    return (last_name.strip(), int(last_line))


def _is_filc_panic(captured_stderr: str) -> bool:
    
    return (
        'filc panic' in captured_stderr
        or 'filc safety error' in captured_stderr
    )


def _report_crash_on_terminal(
    signum:           int,
    captured_stdout:  str,
    captured_stderr:  str,
) -> None:
    
    name = _signal_name(signum)

    if captured_stdout.strip():
        print(captured_stdout, end="")
        if not captured_stdout.endswith("\n"):
            print()

    filc = _is_filc_panic(captured_stderr)

    print()
    info("=" * 60)
    if filc:
        info("FIL-C SAFETY VIOLATION DETECTED")
        info("Fil-C interceptou uma violação de segurança de memória e")
        info("encerrou o processo de forma controlada (Fil-C panic). Esse")
        info("é o comportamento esperado quando o runtime do Fil-C detecta")
        info("acesso a memória inválido — não é um crash não tratado.")
        info("Veja o diagnóstico do Fil-C no stderr abaixo para localizar")
        info("o arquivo, a linha e o ponteiro responsáveis.")
    elif signum == signal.SIGSEGV:
        info(f"TEST PROCESS CRASHED — {name} (segmentation fault)")
        info("A test attempted an invalid memory access (NULL pointer,")
        info("dangling pointer, out-of-bounds, stack overflow, ...).")
    elif signum == signal.SIGABRT:
        info(f"TEST PROCESS ABORTED — {name}")
        info("A test triggered abort() — usually from a failed assert(),")
        info("a stack smash, or a libc consistency check.")
    elif signum == signal.SIGBUS:
        info(f"TEST PROCESS CRASHED — {name} (bus error)")
        info("Possibly a misaligned memory access or a mapped file issue.")
    elif signum == signal.SIGFPE:
        info(f"TEST PROCESS CRASHED — {name} (arithmetic error)")
        info("Possibly a division by zero or invalid floating-point op.")
    else:
        info(f"TEST PROCESS TERMINATED — {name}")

    last = _last_test_before_crash(captured_stdout)
    if last is not None:
        last_name, last_line = last
        info("")
        info(f"Last test reported by Unity: {last_name} (line {last_line})")
        info("The crash occurred either inside this test or in the next one;")
        info("Unity did not get a chance to report further results.")
    else:
        info("")
        info("No test results were reported before the crash;")
        info("the crash likely occurred during setUp() or before main().")

    if captured_stderr.strip():
        info("")
        info("stderr captured from the test process:")
        for line in captured_stderr.rstrip("\n").splitlines():
            print(f"    {line}")

    info("")
    info("Tests after the crash were NOT executed. Fix the issue and re-run.")
    info("=" * 60)
    print()



def _process_captured_unity(captured: str, pdf_collect: list | None) -> bool:
    """
    Parseia stdout Unity capturado, popula pdf_collect com UnitySummary,
    imprime sumário curto no terminal. Retorna True se todos os asserts
    passaram.

    Import lazy do reports — sem --pdf a função não é chamada.
    """
    from .reports import parse_unity_output

    summary = parse_unity_output(captured)
    if pdf_collect is not None:
        pdf_collect.append(summary)

    overall = "OK" if summary.overall_ok else "FAIL"
    passed  = summary.total - summary.failures - summary.ignored
    info(
        f"{summary.total} tests, {passed} passed, "
        f"{summary.failures} failed, {summary.ignored} ignored — {overall}"
    )
    return summary.overall_ok


def run_tests(
    build_dir:   Path,
    target:      str,
    pdf_collect: list | None = None,
) -> bool:
   
    executable = _resolve_executable(build_dir, target)

    info(f"Running tests: {executable}")
    print()

    result = subprocess.run(
        [str(executable), "-v"],
        capture_output=True, text=True,
    )

    signum = _signal_from_returncode(result.returncode)

    # ---------- Caminho 1: crash por sinal ----------
    if signum is not None:
        _report_crash_on_terminal(signum, result.stdout, result.stderr)

        if pdf_collect is not None:
            from .reports import parse_unity_output
            summary = parse_unity_output(result.stdout)
            pdf_collect.append(summary)

        return False

    # ---------- Caminho 2: execução normal (sem crash) ----------
    if pdf_collect is None:
        if result.stdout:
            print(result.stdout, end="")
            if not result.stdout.endswith("\n"):
                print()
        if result.stderr.strip():
            print(result.stderr, end="")
        print()
        return result.returncode == 0

    # Com --pdf: parse e sumário curto, igual ao comportamento anterior.
    _process_captured_unity(result.stdout, pdf_collect)
    return result.returncode == 0


def run_tests_valgrind(
    build_dir:            Path,
    target:               str,
    pdf_collect:          list | None = None,
    pdf_collect_valgrind: list | None = None,
) -> bool:
    
    executable = _resolve_executable(build_dir, target)

    info(f"Running tests under valgrind: {executable}")
    print()

    cmd = [
        "valgrind",
        "--leak-check=full",
        "--show-leak-kinds=all",
        "--track-origins=yes",
        "--error-exitcode=1",
        str(executable),
        "-v",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    signum = _signal_from_returncode(result.returncode)

    # ---------- Crash detectado mesmo sob valgrind (raro mas possível) ----------
    if signum is not None:
        _report_crash_on_terminal(signum, result.stdout, result.stderr)

        if pdf_collect is not None:
            from .reports import parse_unity_output
            pdf_collect.append(parse_unity_output(result.stdout))

        if pdf_collect_valgrind is not None:
            from .reports import parse_valgrind_output
            pdf_collect_valgrind.append(parse_valgrind_output(result.stderr))

        return False

    # ---------- Caminho normal: imprime stdout, depois stderr do valgrind ----------
    if pdf_collect is None:
        # Modo sem --pdf: imprime tudo no terminal.
        if result.stdout:
            print(result.stdout, end="")
            if not result.stdout.endswith("\n"):
                print()
    else:
        # Modo --pdf: sumário curto via parser.
        _process_captured_unity(result.stdout, pdf_collect)

    # Stderr do valgrind sai sempre — é o diagnóstico principal.
    if result.stderr.strip():
        print()
        info("valgrind diagnostics (stderr):")
        print(result.stderr, end="")

    if pdf_collect_valgrind is not None:
        from .reports import parse_valgrind_output

        vg_summary = parse_valgrind_output(result.stderr)
        pdf_collect_valgrind.append(vg_summary)

        status = "clean" if vg_summary.clean else "issues found"
        info(
            f"Valgrind: {vg_summary.error_count} error(s), "
            f"{vg_summary.total_lost_bytes:,} byte(s) lost — {status}"
        )

    return result.returncode == 0


def run_gcovr(
    root:        Path,
    build_dir:   Path,
    test_file:   Path,
    test_dir:    Path,
    src_file:    Path | None = None,
    pdf_collect: list | None = None,
) -> bool:
    
    coverages_dir = root / "coverage"
    coverages_dir.mkdir(exist_ok=True)
    test_coverage_dir = coverages_dir / test_dir.name
    if test_coverage_dir.exists():
        info(f"Deleting {test_coverage_dir}")
        shutil.rmtree(test_coverage_dir)
    test_coverage_dir.mkdir(exist_ok=True)

    html_output    = test_coverage_dir / "index.html"
    json_output    = test_coverage_dir / "summary.json"
    details_output = test_coverage_dir / "details.json"

    filter_args: list[str] = []
    if src_file is not None:
        filter_pattern = re.escape(str(src_file.resolve()))
        filter_args = ["--filter", filter_pattern]
        info(f"Coverage filter: {src_file.name} only (ignoring tests)")
    else:
        info("Coverage filter: none (no --src passed)")

    info("Running gcovr...")
    print()

    subprocess.run([
        "gcovr",
        "--root", str(root),
        *filter_args,
        str(build_dir),
    ])

    subprocess.run([
        "gcovr",
        "--root", str(root),
        *filter_args,
        "--json-summary-pretty",
        "-o", str(json_output),
        str(build_dir),
    ])

    subprocess.run([
        "gcovr",
        "--root", str(root),
        *filter_args,
        "--json", "--json-pretty",
        "-o", str(details_output),
        str(build_dir),
    ])

    subprocess.run([
        "gcovr",
        "--root", str(root),
        *filter_args,
        "--html", "--html-details",
        "-o", str(html_output),
        str(build_dir),
    ])

    print()
    info(f"HTML coverage report saved to: {html_output}")

    if not json_output.exists():
        info("Coverage JSON not generated — treating as incomplete coverage.")
        return False

    try:
        data = json.loads(json_output.read_text())
    except (json.JSONDecodeError, OSError) as e:
        info(f"Could not parse coverage JSON ({e}) — treating as incomplete coverage.")
        return False

    line_percent  = data.get("line_percent")
    lines_total   = data.get("line_total",   0)
    lines_covered = data.get("line_covered", 0)

    if line_percent is None:
        info("Coverage JSON missing 'line_percent' — treating as incomplete coverage.")
        return False

    if lines_total == 0:
        if src_file is not None:
            info(f"WARNING: gcovr reported 0 lines for {src_file.name}. "
                 f"Filter may not match — check src path.")
        else:
            info("WARNING: gcovr reported 0 lines total.")
        return False

    info(f"Coverage: {lines_covered}/{lines_total} lines ({line_percent:.2f}%)")

    if pdf_collect is not None:
        from .reports import parse_coverage_json
        pdf_collect.append(parse_coverage_json(json_output))

    if line_percent >= 100.0:
        info("Coverage: 100% — PASS")
        return True
    else:
        info("Coverage below 100% — FAIL")
        return False


# ----------------------------------------------------------------------------
#  Lizard
# ----------------------------------------------------------------------------

def _lizard_one_file_textual(
    target: Path, label: str, ccn: int, length: int, args: int,
) -> bool:
    """
    Comportamento legado (sem --pdf): roda lizard duas vezes — uma para
    relatório textual no terminal, outra com -w para capturar exit code.
    """
    header = f"─── lizard: {label} ({target.name}) ─────────────────────────────"
    print(header)

    subprocess.run([
        "lizard",
        "-C", str(ccn),
        "-L", str(length),
        "-a", str(args),
        str(target),
    ])

    result = subprocess.run(
        [
            "lizard",
            "-C", str(ccn),
            "-L", str(length),
            "-a", str(args),
            "-w",
            str(target),
        ],
        capture_output=True, text=True,
    )

    print()
    if result.returncode == 0:
        info(f"Lizard [{label}]: all functions within thresholds — PASS")
        print()
        return True
    else:
        if result.stdout.strip():
            info(f"Lizard [{label}] violations:")
            print(result.stdout)
        info(f"Lizard [{label}]: thresholds exceeded — FAIL")
        print()
        return False


def _lizard_one_file_csv(
    target:   Path,
    label:    str,
    ccn:      int,
    length:   int,
    args:     int,
    files_out: list,   # populated with LizardFileReport
) -> bool:
    """
    Modo --pdf: roda lizard --csv, parseia, popula files_out com
    LizardFileReport, imprime sumário curto.
    """
    from .reports import parse_lizard_csv, LizardFileReport

    result = subprocess.run(
        [
            "lizard", "--csv",
            "-C", str(ccn),
            "-L", str(length),
            "-a", str(args),
            str(target),
        ],
        capture_output=True, text=True,
    )
    functions = parse_lizard_csv(result.stdout, ccn, length, args)
    file_report = LizardFileReport(
        label=label, file_path=target, functions=functions,
    )
    files_out.append(file_report)

    if file_report.clean:
        info(f"Lizard [{label}]: {file_report.total_functions} functions, "
             f"all within thresholds — PASS")
        return True
    else:
        info(f"Lizard [{label}]: {file_report.total_functions} functions, "
             f"{file_report.violating_functions} violations — FAIL")
        return False


def run_lizard(
    test_file:   Path,
    src_file:    Path | None,
    ccn:         int = DEFAULT_LIZARD_CCN,
    length:      int = DEFAULT_LIZARD_LENGTH,
    args:        int = DEFAULT_LIZARD_ARGS,
    pdf_collect: list | None = None,
) -> bool:
    
    if pdf_collect is None:
        info(f"Lizard thresholds: CCN <= {ccn}, length <= {length}, args <= {args}")
        print()

        test_ok = _lizard_one_file_textual(test_file, label="test",
                                           ccn=ccn, length=length, args=args)
        src_ok = True
        if src_file is not None:
            src_ok = _lizard_one_file_textual(src_file, label="src",
                                              ccn=ccn, length=length, args=args)

        overall = test_ok and src_ok
        info("Lizard: overall PASS" if overall else "Lizard: overall FAIL")
        return overall

    # Modo --pdf
    from .reports import LizardSummary

    info(f"Lizard thresholds: CCN <= {ccn}, length <= {length}, args <= {args}")

    files_out: list = []
    test_ok = _lizard_one_file_csv(test_file, "test", ccn, length, args, files_out)
    src_ok = True
    if src_file is not None:
        src_ok = _lizard_one_file_csv(src_file, "src", ccn, length, args, files_out)

    summary = LizardSummary(
        files=files_out, ccn_th=ccn, length_th=length, args_th=args,
    )
    pdf_collect.append(summary)

    overall = test_ok and src_ok
    info("Lizard: overall PASS" if overall else "Lizard: overall FAIL")
    return overall