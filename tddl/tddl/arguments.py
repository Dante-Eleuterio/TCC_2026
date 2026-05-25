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
from .run import (
    DEFAULT_LIZARD_CCN,
    DEFAULT_LIZARD_LENGTH,
    DEFAULT_LIZARD_ARGS,
)


def _parse_int_flag(args: list[str], flag_prefix: str, use_lizard: bool, default: int) -> int:
    """
    Procura uma flag no formato '<flag_prefix>N' (e.g. '--ccn=10') na lista
    de args, valida que o valor é um inteiro >= 1, e retorna o valor
    parseado. Se a flag não estiver presente, retorna `default`.

    Falha (via die) se:
      - a flag estiver presente mas sem valor numérico válido
      - a flag estiver presente sem --lizard (não teria efeito)

    Padrão `--<nome>=<valor>` é o mesmo para todas as flags de threshold,
    então extraí esta função pra evitar três cópias quase idênticas.
    """
    found = next((a for a in args if a.startswith(flag_prefix)), None)
    if found is None:
        return default

    value_str = found[len(flag_prefix):]
    if not value_str:
        die(f"{flag_prefix} requires a numeric value. e.g. {flag_prefix}10")

    try:
        value = int(value_str)
    except ValueError:
        die(f"{flag_prefix} must be an integer, got: {value_str!r}")

    if value < 1:
        die(f"{flag_prefix} must be >= 1, got: {value}")

    if not use_lizard:
        die(f"{flag_prefix}N has no effect without --lizard. "
            f"Add --lizard or remove {flag_prefix}.")

    return value


def parse_args() -> tuple[str, bool, bool, bool, bool, int, int, int, str, bool, list[str]]:
   
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("USAGE GUIDE FOR TDDL \n")

        print("Build: $tddl build")
        print(
            "  -Run from the project root to generate expected structure.\n"
            "  -It will not override any existing include/ , src/ or tests/ folders \n"
            "  Built structure:\n"
            "    project/        <- run tddl from here\n"
            "    ├── include/    <- public headers (.h)\n"
            "    ├── src/        <- reserved for future use\n"
            "    └── tests/      <- where your test_file.c go\n"
        )
        print("Usage: $tddl <test_file.c> ")
        print("  -Run from the project root. tddl looks for the file in <cwd>/tests/")
        print("  -UNITY_PATH must be set in your environment.")
        print(
            "  Expected structure:\n"
            "    project/        <- run tddl from here\n"
            "    ├── include/    <- public headers (.h)\n"
            "    ├── src/        <- reserved for future use\n"
            "    └── tests/\n"
            "        └── test01.c\n"
        )
        print("Usage: $tddl <test_file.c> --src <source_file.c>")
        print("  -Links a separate source file from src/ into the test build\n")

        print("Usage: $tddl <test_file.c> --coverage")
        print("  -Runs all tests and then uses gcovr for coverage tests \n")

        print("Usage: $tddl <test_file.c> --filc")
        print("  -Compiles test with filc and then runs all tests \n")

        print("Usage: $tddl <test_file.c> --valgrind")
        print("  -Runs tests under valgrind with strict memory checks\n")
        print("  -CANNOT be combined with --filc\n")

        print("Usage: $tddl <test_file.c> --lizard [--ccn=N] [--length=N] [--args=N]")
        print("  -Runs lizard static analysis on the test file (and --src file, if passed)\n")
        print(
            f"  -Default thresholds: "
            f"CCN <= {DEFAULT_LIZARD_CCN}, "
            f"length <= {DEFAULT_LIZARD_LENGTH}, "
            f"args <= {DEFAULT_LIZARD_ARGS}\n"
        )
        print("  -Override thresholds individually:\n"
              "      --ccn=N      max cyclomatic complexity per function\n"
              "      --length=N   max lines per function\n"
              "      --args=N     max parameters per function\n")
        print("  -If any function exceeds the thresholds, tddl exits with code != 0\n")
        print("  -Can be combined with any other flag\n")
        print("  -Requires lizard installed: pip install lizard")
        sys.exit(0)
       
    filename     = args[0]
    use_filc     = "--filc"     in args
    use_coverage = "--coverage" in args
    use_valgrind = "--valgrind" in args
    use_lizard   = "--lizard"   in args

    if use_filc and use_coverage:
        die("--filc and --coverage cannot be used together")
    if use_filc and use_valgrind:
        die(
            "--filc and --valgrind cannot be used together.\n"
            "  Fil-C enforces memory safety at compile time, which makes valgrind redundant\n"
            "  and produces false positives on Fil-C's runtime metadata.\n"
            "  Pick one: --filc (compile-time safety) OR --valgrind (runtime safety)."
        )

    # ------------------------------------------------------------------
    # Thresholds do lizard, todos com sintaxe --<name>=<int>
    # ------------------------------------------------------------------
    ccn    = _parse_int_flag(args, "--ccn=",    use_lizard, DEFAULT_LIZARD_CCN)
    length = _parse_int_flag(args, "--length=", use_lizard, DEFAULT_LIZARD_LENGTH)
    args_  = _parse_int_flag(args, "--args=",   use_lizard, DEFAULT_LIZARD_ARGS)

    src_file = None
    if "--src" in args:
        src_index = args.index("--src")
        if src_index + 1 >= len(args):
            die("--src requires a filename argument. e.g. --src constroi_nome.c")
        src_file = args[src_index + 1]

    if args[0] in ["--build"]:
        build_structure = True
    else:
        build_structure = False
    
    include_files = []

    if "--include" in args:
        idx = args.index("--include")

        if idx + 1 >= len(args):
            raise ValueError("--include requires a files lists separeted by comma. Example: --include mocks.c, helpers.c")

        include_arg = args[idx + 1]

        include_files = []

        for f in include_arg.split(","):
            if f.strip():
                include_files.append(f.strip())

    return (filename, use_filc, use_coverage, use_valgrind, use_lizard,
            ccn, length, args_, src_file, build_structure,include_files)