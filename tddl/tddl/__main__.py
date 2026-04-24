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

Usage:
    tddl test_constroi_nome.c

    Run from the project root directory. tddl will look for the test file at:
        <cwd>/tests/test_constroi_nome.c

Expects:
    - UNITY_PATH environment variable pointing to the Unity root directory
    - Project structure:
        project/          <- run tddl from here
        ├── include/      <- public headers (.h)
        ├── src/          <- source code
        └── tests/
            ├── test_constroi_nome.c   <- user-created test file
            └── CMakeLists.txt         <- generated once by tddl
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
    filename, use_filc, use_coverage, use_valgrind, src_arg = parse_args()

    check_tools(use_coverage, use_valgrind)
    filc = get_filc_path() if use_filc else None

    unity                     = get_unity_path()
    root, test_dir, test_file = resolve_paths(filename)
    src_file = resolve_src_file(root, src_arg) if src_arg else None
    ensure_structure(root)
    target     = f"tddl_{test_file.stem}"
    wrap_funcs = extract_wrap_funcs(test_file)

    build_dir = Path(tempfile.mkdtemp(prefix="tddl_build_"))

    # Compose mode description. --valgrind can combine with --coverage,
    # so we build the label from parts.
    if use_filc:
        mode = "Fil-C (memory-safe)"
    else:
        parts = ["gcc"]
        if use_valgrind:
            parts.append("valgrind")
        if use_coverage:
            parts.append("coverage")
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
    coverage_full = True   # só vira False se --coverage rodar e der <100%

    try:
        cmake_configure(test_dir, build_dir)
        cmake_build(build_dir, target)

        # Valgrind wraps the test runner; when --error-exitcode=1 is set,
        # a memory error makes the process exit !=0 and tests_passed=False,
        # even if every Unity assertion passed.
        if use_valgrind:
            tests_passed = run_tests_valgrind(build_dir, target)
        else:
            tests_passed = run_tests(build_dir, target)

        if use_coverage:
            if not tests_passed:
                info("Tests FAILED — skipping gcovr.")
                coverage_full = False
            else:
                coverage_full = run_gcovr(root, build_dir, test_file, test_dir)
        elif not tests_passed:
            info("Tests FAILED ")

    finally:
        cleanup(build_dir)

    # Final exit code logic:
    #   - Tests must always pass (Unity asserts + valgrind clean if applicable).
    #   - With --coverage, also require 100% line coverage.
    if use_coverage:
        success = tests_passed and coverage_full
    else:
        success = tests_passed

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()