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


def run_tests(build_dir: Path, target: str) -> bool:
    executable = _resolve_executable(build_dir, target)

    info(f"Running tests: {executable}")
    print()
    result = subprocess.run([str(executable), "-v"])
    print()
    return result.returncode == 0


def run_tests_valgrind(build_dir: Path, target: str) -> bool:
    executable = _resolve_executable(build_dir, target)

    info(f"Running tests under valgrind: {executable}")
    print()
    result = subprocess.run([
        "valgrind",
        "--leak-check=full",
        "--show-leak-kinds=all",
        "--track-origins=yes",
        "--error-exitcode=1",
        str(executable),
        "-v",
    ])
    print()
    return result.returncode == 0


def run_gcovr(
    root:      Path,
    build_dir: Path,
    test_file: Path,
    test_dir:  Path,
    src_file:  Path | None = None,
) -> bool:
    """
    Roda o gcovr e retorna True se a cobertura de linhas for 100%.

    Quando src_file é fornecido, o gcovr é restrito a esse arquivo via
    --filter. Cobertura de arquivos de teste, headers do Unity, etc.,
    é ignorada — apenas o código de produção é medido. Sem src_file
    (estrutura A, código embutido no test_file), mede o test_file
    direto, mas isso geralmente dá 100% trivialmente.

    Sempre gera:
      - resumo em texto no terminal
      - summary.json (lido para decidir pass/fail)
      - relatório HTML em project/coverage/<test_dir>/index.html
    """
    coverages_dir = root / "coverage"
    coverages_dir.mkdir(exist_ok=True)
    test_coverage_dir = coverages_dir / test_dir.name
    if test_coverage_dir.exists():
        info(f"Deleting {test_coverage_dir}")
        shutil.rmtree(test_coverage_dir)
    test_coverage_dir.mkdir(exist_ok=True)

    html_output = test_coverage_dir / "index.html"
    json_output = test_coverage_dir / "summary.json"

    # Filtro: quando há src_file, restringimos a análise a ele.
    # gcovr aceita --filter <regex>; usamos re.escape para tratar o
    # path como literal (evita interpretação de "." e outros metachars).
    filter_args: list[str] = []
    if src_file is not None:
        filter_pattern = re.escape(str(src_file.resolve()))
        filter_args = ["--filter", filter_pattern]
        info(f"Coverage filter: {src_file.name} only (ignoring tests)")
    else:
        info("Coverage filter: none (no --src passed)")

    info("Running gcovr...")
    print()

    # Terminal summary
    subprocess.run([
        "gcovr",
        "--root", str(root),
        *filter_args,
        str(build_dir),
    ])

    # JSON summary
    subprocess.run([
        "gcovr",
        "--root", str(root),
        *filter_args,
        "--json-summary-pretty",
        "-o", str(json_output),
        str(build_dir),
    ])

    # HTML report
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

    # Caso edge: --filter pode não bater em nada se o build dir não tiver
    # gcov data do src_file (improvável, mas vale alertar em vez de
    # silenciosamente reportar 100%).
    if lines_total == 0:
        if src_file is not None:
            info(f"WARNING: gcovr reported 0 lines for {src_file.name}. "
                 f"Filter may not match — check src path.")
        else:
            info("WARNING: gcovr reported 0 lines total.")
        return False

    info(f"Coverage: {lines_covered}/{lines_total} lines ({line_percent:.2f}%)")

    if line_percent >= 100.0:
        info("Coverage: 100% — PASS")
        return True
    else:
        info("Coverage below 100% — FAIL")
        return False


def _lizard_one_file(target: Path, label: str, ccn: int, length: int, args: int) -> bool:
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
        capture_output=True,
        text=True,
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


def run_lizard(
    test_file: Path,
    src_file:  Path | None,
    ccn:       int = DEFAULT_LIZARD_CCN,
    length:    int = DEFAULT_LIZARD_LENGTH,
    args:      int = DEFAULT_LIZARD_ARGS,
) -> bool:
    info(
        f"Lizard thresholds: CCN <= {ccn}, "
        f"length <= {length}, "
        f"args <= {args}"
    )
    print()

    test_ok = _lizard_one_file(test_file, label="test",
                               ccn=ccn, length=length, args=args)
    src_ok  = True
    if src_file is not None:
        src_ok = _lizard_one_file(src_file, label="src",
                                  ccn=ccn, length=length, args=args)

    overall = test_ok and src_ok
    if overall:
        info("Lizard: overall PASS")
    else:
        info("Lizard: overall FAIL")
    return overall