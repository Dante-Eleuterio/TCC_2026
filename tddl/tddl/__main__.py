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
from pathlib import Path
from .arguments import *
from .cmakes import *
from .enviroment import *
from .helpers import *
from .path import *
from .run import *


def main() -> None:
    (filename, use_filc, use_coverage, use_valgrind, use_lizard,
     ccn, length, args_threshold, src_arg, build_structure) = parse_args()

        
    check_tools(use_coverage, use_valgrind, use_lizard)
    filc = get_filc_path() if use_filc else None

    root = get_root()
    if build_structure:
        ensure_structure(root)
        sys.exit(0)

    unity                     = get_unity_path()
    root, test_dir, test_file = resolve_paths(filename)
    src_file = resolve_src_file(root, src_arg) if src_arg else None
    ensure_structure(root)
    target     = f"tddl_{test_file.stem}"
    wrap_funcs = extract_wrap_funcs(test_file)

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
    )

    tests_passed  = False
    coverage_full = True
    lizard_clean  = True

    try:
        cmake_configure(test_dir, build_dir)
        cmake_build(build_dir, target)

        if use_valgrind:
            tests_passed = run_tests_valgrind(build_dir, target)
        else:
            tests_passed = run_tests(build_dir, target)

        if use_coverage:
            if not tests_passed:
                info("Tests FAILED — skipping gcovr.")
                coverage_full = False
            else:
                # Passamos src_file ao gcovr: quando presente, ele
                # filtra a cobertura para considerar apenas o código
                # de produção (ignora test_file e dependências).
                coverage_full = run_gcovr(
                    root, build_dir, test_file, test_dir,
                    src_file=src_file,
                )
        elif not tests_passed:
            info("Tests FAILED ")

        if use_lizard:
            lizard_clean = run_lizard(
                test_file, src_file,
                ccn=ccn, length=length, args=args_threshold,
            )

    finally:
        cleanup(build_dir)

    success = tests_passed
    if use_coverage:
        success = success and coverage_full
    if use_lizard:
        success = success and lizard_clean

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()