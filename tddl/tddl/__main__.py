#!/usr/bin/env python3
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
"""
tddl - TDD launcher for Unity-based C tests with gcovr coverage.
"""
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from .arguments import *
from .cmakes import *
from .enviroment import *
from .helpers import *
from .path import *
from .run import *


def main() -> None:
    (filename, use_filc, use_coverage, use_valgrind, use_lizard,
     ccn, length, args_threshold, src_arg, build_structure, include_raw_list,
     use_pdf, build_filc, run_doctor_flag) = parse_args()

    root = get_root()

    # Modos de setup/diagnóstico. Cada um sai antes de qualquer checagem
    # de teste/tools, porque o objetivo deles é exatamente preparar ou
    # inspecionar o ambiente.
    if run_doctor_flag:
        from .installer import run_doctor
        sys.exit(run_doctor(root))

    if build_structure:
        from .installer import run_build
        run_build(root)
        sys.exit(0)

    if build_filc:
        from .installer import run_build_filc
        run_build_filc(root)
        sys.exit(0)

    check_tools(use_coverage, use_valgrind, use_lizard, use_pdf)
    filc = get_filc_path(root) if use_filc else None

    unity                     = get_unity_path(root)

    ensure_structure(root)
    root, test_dir, test_file = resolve_paths(filename)
    src_file = resolve_src_file(root, src_arg) if src_arg else None
    include_paths_list = find_includes(root, include_raw_list)

    target = f"tddl_{test_file.stem}"

    files_to_scan = [test_file]
    if src_file:
        files_to_scan.append(src_file)
    files_to_scan.extend(include_paths_list)

    wrap_funcs = extract_wrap_funcs(files_to_scan)

    build_dir = Path(tempfile.mkdtemp(prefix="tddl_build_"))

    # Compose mode description.
    if use_filc:
        parts = ["Fil-C (memory-safe)"]
    else:
        parts = ["gcc"]
        if use_valgrind:
            parts.append("valgrind")
        if use_coverage:
            parts.append("coverage")
    if use_lizard:
        parts.append(f"lizard(ccn={ccn},length={length},args={args_threshold})")
    if use_pdf:
        parts.append("pdf")
    mode = " + ".join(parts) if len(parts) > 1 else parts[0]

    info(f"Project  : {root}")
    info(f"Test file: {test_file}")
    info(f"Unity    : {unity}")
    info(f"Target   : {target}")
    info(f"Mode     : {mode}")
    info(f"Build    : {build_dir}")
    print()

    generate_cmakelists(
        root, test_dir, test_file, unity,
        use_coverage, use_filc, filc, src_file, wrap_funcs,
        include_paths_list
    )

    # ---------------- PDF setup ----------------
    # Quando --pdf está ativo, as funções run_* recebem listas onde
    # depositam seus Summary objects. Depois de tudo rodar, montamos
    # o PDF combinado chamando reports.generate_combined_pdf.
    #
    # Path: <project>/reports/<test_stem>/report.pdf
    # (genérico — não "tests.pdf" porque o relatório agora cobre todas
    # as ferramentas, não só os testes Unity)
    report_pdf_path: Path | None = None
    unity_pdf_list:    list = []
    lizard_pdf_list:   list = []
    valgrind_pdf_list: list = []
    run_dt = datetime.now()   # timestamp consistente entre logs e PDF

    if use_pdf:
        report_pdf_path = root / "reports" / test_file.stem / "report.pdf"

    tests_passed  = False
    coverage_full = True
    lizard_clean  = True

    try:
        cmake_configure(test_dir, build_dir)
        cmake_build(build_dir, target)

        if use_valgrind:
            tests_passed = run_tests_valgrind(
                build_dir, target,
                pdf_collect=(unity_pdf_list if use_pdf else None),
                pdf_collect_valgrind=(valgrind_pdf_list if use_pdf else None),
            )
        else:
            tests_passed = run_tests(
                build_dir, target,
                pdf_collect=(unity_pdf_list if use_pdf else None),
            )

        if use_coverage:
            # gcovr filtra a cobertura ao src_file quando presente,
            # ignorando arquivos de teste.
            coverage_full = run_gcovr(
                root, build_dir, test_file, test_dir,
                src_file=src_file,
            )
        elif not tests_passed:
            info("Tests FAILED")

        if use_lizard:
            lizard_clean = run_lizard(
                test_file, src_file,
                ccn=ccn, length=length, args=args_threshold,
                pdf_collect=(lizard_pdf_list if use_pdf else None),
            )

    finally:
        cleanup(build_dir)

    # ---------------- Geração do PDF combinado ----------------
    # Mesmo se alguma ferramenta tiver falhado, geramos o PDF com o que
    # foi coletado — o PDF é diagnóstico, não cabe a ele exigir sucesso.
    # Cada summary é None se a ferramenta não rodou ou não populou nada.
    if use_pdf:
        from .reports import generate_combined_pdf

        unity_summary    = unity_pdf_list[0]    if unity_pdf_list    else None
        lizard_summary   = lizard_pdf_list[0]   if lizard_pdf_list   else None
        valgrind_summary = valgrind_pdf_list[0] if valgrind_pdf_list else None

        generate_combined_pdf(
            output_path=report_pdf_path,
            test_file=test_file,
            src_file=src_file,
            mode=mode,
            run_dt=run_dt,
            unity=unity_summary,
            lizard=lizard_summary,
            valgrind=valgrind_summary,
        )
        info(f"PDF report: {report_pdf_path}")

    success = tests_passed
    if use_coverage:
        success = success and coverage_full
    if use_lizard:
        success = success and lizard_clean

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()