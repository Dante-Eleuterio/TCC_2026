# BSD 2-Clause License
#
# Copyright (c) 2026, Dante Eleutério dos Santos
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
#  Padrão de out-parameter para coleta de summaries
# ----------------------------------------------------------------------------
#
# Quando `--pdf` está ativo, o __main__ cria uma lista por ferramenta e
# passa adiante. Cada `run_*` faz `out.append(summary)` se for chamado.
# No final, o __main__ chama generate_combined_pdf com tudo que foi
# coletado.
#
# Esse padrão tem duas vantagens sobre mudar o tipo de retorno:
#   1. Não quebra callers existentes (retorno continua sendo bool).
#   2. Funções podem opcionalmente popular múltiplos summaries (ex: lizard
#      adiciona test_file e src_file separados, então usa list mesmo).
#
# Quando `pdf_collect` é None (modo sem --pdf), não capturamos a saída;
# tudo segue ao vivo no terminal como antes.
# ----------------------------------------------------------------------------


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
    """
    Roda o executável de testes Unity.

    pdf_collect=None  -> comportamento clássico: output ao vivo no terminal.
    pdf_collect=[]    -> captura stdout, popula list com UnitySummary,
                          imprime só sumário curto.
    """
    executable = _resolve_executable(build_dir, target)

    info(f"Running tests: {executable}")
    print()

    if pdf_collect is None:
        result = subprocess.run([str(executable), "-v"])
        print()
        return result.returncode == 0

    result = subprocess.run(
        [str(executable), "-v"],
        capture_output=True, text=True,
    )
    # Em modo --pdf, exit code do Unity é a fonte da verdade para
    # tests_passed (não confunde com erro de parsing).
    _process_captured_unity(result.stdout, pdf_collect)
    return result.returncode == 0


def run_tests_valgrind(
    build_dir:            Path,
    target:               str,
    pdf_collect:          list | None = None,
    pdf_collect_valgrind: list | None = None,
) -> bool:
    """
    Roda sob valgrind. --error-exitcode=1 garante exit !=0 em erro de
    memória mesmo com testes Unity ok.

    pdf_collect           -> populado com UnitySummary  (stdout do binário)
    pdf_collect_valgrind  -> populado com ValgrindSummary (stderr do valgrind)

    Em modo --pdf (qualquer das duas listas != None), captura saída
    completa; sem --pdf, comportamento clássico de output ao vivo.
    """
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

    capture = (pdf_collect is not None) or (pdf_collect_valgrind is not None)

    if not capture:
        result = subprocess.run(cmd)
        print()
        return result.returncode == 0

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Unity (stdout) — sumário curto + populate pdf_collect.
    if pdf_collect is not None:
        _process_captured_unity(result.stdout, pdf_collect)

    # Valgrind (stderr) — sempre mostra ao usuário no terminal pra não
    # esconder os diagnósticos; em modo --pdf, também parseia.
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
    """
    Roda o gcovr e retorna True se a cobertura de linhas for 100%.

    Quando src_file é fornecido, o gcovr é restrito a esse arquivo via
    --filter. Sempre gera resumo no terminal, summary.json, e relatório
    HTML em project/coverage/<test_dir>/index.html.

    pdf_collect=None  -> comportamento clássico.
    pdf_collect=[]    -> além de gerar tudo o que já gerava, parseia o
                          summary.json e popula a lista com CoverageSummary
                          para a geração do PDF combinado.
    """
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

    # JSON detalhado: contém o array `lines` por arquivo, necessário pra
    # identificar quais linhas específicas não foram cobertas. Gerado em
    # paralelo ao summary; parse_coverage_json no reports.py vai
    # consumi-lo automaticamente se existir.
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

    # Em modo --pdf, parseamos o summary.json em uma estrutura tipada
    # para a seção de Coverage do relatório consolidado. Reaproveitamos
    # o mesmo JSON que acabamos de produzir.
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
    """
    Roda lizard no test_file e (opcionalmente) no src_file.

    pdf_collect=None  -> imprime relatório textual no terminal.
    pdf_collect=[]    -> roda em modo CSV silencioso, popula com
                          LizardSummary (uma única entrada que contém
                          os LizardFileReport por arquivo).
    """
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