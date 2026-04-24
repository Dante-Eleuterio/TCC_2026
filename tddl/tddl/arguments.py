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
import sys
from .helpers import *

def parse_args() -> tuple[str, bool, bool, bool, str | None]:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("USAGE GUIDE FOR TDDL \n")

        print("Build: $tddl build")
        print(
            "  -Run from the project root to generate expected structure.\n"
            "  -It will not override any existing include/ , src/ or tests/ folders "
            "\n"
            "  Built structure:\n"
            "    project/        <- run tddl from here\n"
            "    ├── include/    <- public headers (.h)\n"
            "    ├── src/        <- reserved for future use\n"
            "    └── tests/      <- where <test_file>/<test_file>.c\n"
        )
        print("Usage: $tddl <test_file.c> ")
        print("  -Run from the project root. tddl looks for the file in <cwd>/tests/")
        print("  -UNITY_PATH must be set in your environment.")
        print("  -WILL CREATE A NEW CMAKESLIST.TXT IN THE SAME FOLDER OF TEST_NAME.C. IT WILL DELETE ANY OLD CMAKESLIST.TXT")
        print(
            "  Expected structure:\n"
            "    project/        <- run tddl from here\n"
            "    ├── include/    <- public headers (.h)\n"
            "    ├── src/        <- reserved for future use\n"
            "    └── tests/\n"
            "        └── test01/\n"
            "            └── test01.c\n"
        )
        print("Usage: $tddl <test_file.c> --src <source_file.c>")
        print("  -Links a separate source file from src/ into the test build\n")
        print("  -tddl resolves the source file relative to <cwd>/src/\n")
        print("  -WILL CREATE A NEW CMAKESLIST.TXT IN THE SAME FOLDER OF TEST_NAME.C. IT WILL DELETE ANY OLD CMAKESLIST.TXT")
        print(
            "  Expected structure:\n"
            "    project/\n"
            "    ├── include/\n"
            "    │   └── constroi_nome.h\n"
            "    │   └── fotomosaico.h\n"
            "    ├── src/\n"
            "    │   └── fotomosaico.c    <- pure source, no tests\n"
            "    └── tests/\n"
            "        └── constroi_nome/\n"
            "            └── constroi_nome.c <- tests only\n"
        )
        print("Usage: $tddl <test_file.c> --coverage")
        print("  -Expects same project structure as in normal usage\n")
        print("  -Runs all tests and then uses gcovr for coverage tests \n")
        print("  -Creates project/coverage folder \n")
        print("  -WILL CREATE A NEW CMAKESLIST.TXT IN THE SAME FOLDER OF TEST_NAME.C. IT WILL DELETE ANY OLD CMAKESLIST.TXT")

        print("Usage: $tddl <test_file.c> --filc")
        print("  -Expects same project structure as in normal usage\n")
        print("  -Compiles test with filc and then runs all tests \n")
        print("  -WILL CREATE A NEW CMAKESLIST.TXT IN THE SAME FOLDER OF TEST_NAME.C. IT WILL DELETE ANY OLD CMAKESLIST.TXT")

        print("Usage: $tddl <test_file.c> --valgrind")
        print("  -Expects same project structure as in normal usage\n")
        print("  -Runs tests under valgrind with: --leak-check=full --show-leak-kinds=all --track-origins=yes --error-exitcode=1\n")
        print("  -Any memory error detected by valgrind makes tddl exit with code != 0\n")
        print("  -Can be combined with --coverage (valgrind runs the test; gcovr is run afterwards)\n")
        print("  -CANNOT be combined with --filc (Fil-C already enforces memory safety at compile time;\n"
              "   running valgrind on Fil-C binaries produces false positives)\n")
        print("  -WILL CREATE A NEW CMAKESLIST.TXT IN THE SAME FOLDER OF TEST_NAME.C. IT WILL DELETE ANY OLD CMAKESLIST.TXT")
        sys.exit(0)

    filename     = args[0]
    use_filc     = "--filc"     in args
    use_coverage = "--coverage" in args
    use_valgrind = "--valgrind" in args

    if use_filc and use_coverage:
        die("--filc and --coverage cannot be used together")
    if use_filc and use_valgrind:
        die(
            "--filc and --valgrind cannot be used together.\n"
            "  Fil-C enforces memory safety at compile time, which makes valgrind redundant\n"
            "  and produces false positives on Fil-C's runtime metadata.\n"
            "  Pick one: --filc (compile-time safety) OR --valgrind (runtime safety)."
        )

    src_file = None
    if "--src" in args:
        src_index = args.index("--src")
        if src_index + 1 >= len(args):
            die("--src requires a filename argument. e.g. --src constroi_nome.c")
        src_file = args[src_index + 1]

    return filename, use_filc, use_coverage, use_valgrind, src_file