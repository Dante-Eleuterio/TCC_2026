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
import subprocess
from pathlib import Path
from .helpers import die, info
import shutil



def run_tests(build_dir: Path, target: str) -> bool:
    executable = build_dir / target
    if not executable.exists():
        candidates = list(build_dir.rglob(target))
        if not candidates:
            die(f"Test executable not found after build: {target}")
        executable = candidates[0]

    info(f"Running tests: {executable}")
    print()
    # -v (verbose) faz o Unity imprimir cada teste individualmente
    # com seu resultado (PASS/FAIL/IGNORE), em vez de só o resumo final.
    result = subprocess.run([str(executable), "-v"])
    print()
    return result.returncode == 0

def run_gcovr(root: Path, build_dir: Path, test_file: Path, test_dir: Path) -> bool:
    """
    Roda o gcovr em três passos:
      1. Resumo em texto no terminal.
      2. JSON summary (usado para decidir se a cobertura é 100%).
      3. Relatório HTML salvo em project/coverage/<test_dir>/index.html.

    Retorna True se a cobertura de linhas for 100%, False caso contrário.
    Se o gcovr falhar em gerar/parsear o JSON, retorna False (tratado como
    cobertura incompleta) para que o ctest reporte falha em vez de passar
    falsamente.
    """
    coverages_dir = root / "coverage"
    coverages_dir.mkdir(exist_ok=True)
    test_coverage_dir = coverages_dir / test_dir.name
    if test_coverage_dir.exists():
        info(f"Deleting {test_coverage_dir}")
        shutil.rmtree(test_coverage_dir)  # deletes everything inside
    test_coverage_dir.mkdir(exist_ok=True)

    html_output = test_coverage_dir / "index.html"
    json_output = test_coverage_dir / "summary.json"

    info("Running gcovr...")
    print()

    # Terminal summary
    subprocess.run([
        "gcovr",
        "--root", str(root),
        str(build_dir),
    ])

    # JSON summary — usado para decidir pass/fail pela cobertura
    subprocess.run([
        "gcovr",
        "--root", str(root),
        "--json-summary-pretty",
        "-o", str(json_output),
        str(build_dir),
    ])

    # HTML report
    subprocess.run([
        "gcovr",
        "--root", str(root),
        "--html", "--html-details",
        "-o", str(html_output),
        str(build_dir),
    ])

    print()
    info(f"HTML coverage report saved to: {html_output}")

    # ------------------------------------------------------------------
    # Parse do JSON e decisão sobre cobertura total
    # ------------------------------------------------------------------
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

    info(f"Coverage: {lines_covered}/{lines_total} lines ({line_percent:.2f}%)")

    # gcovr emite 100.0 somente quando todas as linhas executáveis foram
    # cobertas. Qualquer linha não coberta resulta em um valor estritamente
    # menor, portanto a comparação direta é segura.
    if line_percent >= 100.0:
        info("Coverage: 100% — PASS")
        return True
    else:
        info("Coverage below 100% — FAIL")
        return False