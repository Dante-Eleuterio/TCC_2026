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


# Thresholds padrão para --lizard.
# Todos podem ser sobrescritos pelo usuário via:
#   --ccn=N      complexidade ciclomática
#   --length=N   linhas máximas por função
#   --args=N     parâmetros máximos por função
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
    # -v faz o Unity imprimir cada teste individualmente (PASS/FAIL).
    result = subprocess.run([str(executable), "-v"])
    print()
    return result.returncode == 0


def run_tests_valgrind(build_dir: Path, target: str) -> bool:
    """
    Roda o executável de teste sob valgrind com checks de memória estritos.

    Valgrind é configurado com --error-exitcode=1, o que faz o processo sair
    com 1 se algum erro de memória for detectado (vazamento, uso de memória
    não inicializada, escrita fora dos limites, etc.), mesmo que os asserts
    do Unity tenham passado.

    Com isso, o retorno desta função reflete simultaneamente:
      - exit code do Unity (testes falharam → !=0)
      - exit code injetado por valgrind (erro de memória → !=0)
    """
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

    if line_percent >= 100.0:
        info("Coverage: 100% — PASS")
        return True
    else:
        info("Coverage below 100% — FAIL")
        return False


def _lizard_one_file(target: Path, label: str, ccn: int, length: int, args: int) -> bool:
    """
    Roda lizard em um único arquivo e retorna True se estiver dentro dos
    thresholds, False caso contrário.

    Duas chamadas:
      1. Relatório completo (todas as funções) — exibido ao usuário.
      2. Modo strict (-w) — apenas para capturar o exit code limpo.
    """
    header = f"─── lizard: {label} ({target.name}) ─────────────────────────────"
    print(header)

    # 1. Relatório completo
    subprocess.run([
        "lizard",
        "-C", str(ccn),
        "-L", str(length),
        "-a", str(args),
        str(target),
    ])

    # 2. Modo "warnings only" para capturar o exit code
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
    """
    Roda lizard separadamente em cada arquivo de interesse:
      - test_file (sempre)
      - src_file  (se --src foi passado)

    Cada arquivo recebe seu próprio cabeçalho na saída, deixando claro
    qual relatório pertence a qual arquivo.

    Parâmetros (todos com defaults — sobrescritos via CLI):
      ccn    : threshold de complexidade ciclomática     (--ccn=N)
      length : threshold de linhas por função            (--length=N)
      args   : threshold de parâmetros por função        (--args=N)

    Retorna True se ambos passarem nos thresholds, False se qualquer um
    exceder.
    """
    info(
        f"Lizard thresholds: CCN <= {ccn}, "
        f"length <= {length}, "
        f"args <= {args}"
    )
    print()

    # Avalia AMBOS antes de retornar — assim o usuário vê os dois relatórios
    # mesmo quando o primeiro já falhou (útil pra refatorar tudo de uma vez).
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