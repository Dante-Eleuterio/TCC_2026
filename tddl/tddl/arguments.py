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


def parse_args() -> tuple[str, bool, bool, bool, bool, int, int, int, str, bool, list[str], bool, bool, bool]:
   
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(
            "tddl — TDD launcher for Unity-based C tests.\n"
            "       Runs your tests, optionally under valgrind, with gcovr coverage,\n"
            "       lizard complexity analysis, Fil-C memory safety, and a combined\n"
            "       PDF report.\n"
        )

        print("SETUP")
        print("─" * 60)
        print()
        print("  tddl --build")
        print(
            "      Bootstrap the project. Idempotent — safe to re-run.\n"
            "        • Installs cmake, valgrind, git and a C compiler via your\n"
            "          system package manager (apt / dnf / pacman / brew).\n"
            "        • Installs lizard and gcovr via pipx; reportlab via pip.\n"
            "        • Clones Unity into ./vendor/unity/.\n"
            "        • Creates include/, src/, tests/ if they don't exist.\n"
            "        • Adds vendor/, reports/, coverage/ to .gitignore.\n"
            "      Resulting layout:\n"
            "        project/        <- run tddl from here\n"
            "        ├── include/    <- public headers (.h)\n"
            "        ├── src/        <- implementation (.c)\n"
            "        ├── tests/      <- your test files (.c)\n"
            "        └── vendor/     <- Unity and (optionally) Fil-C\n"
        )
        print("  tddl --build-filc")
        print(
            "      Build Fil-C into ./vendor/filc/. Takes 30–60 minutes and\n"
            "      uses ~10–20 GB of disk. Only needed for --filc.\n"
            "      Run `tddl --build` first to install prerequisites.\n"
        )

        print("DIAGNOSTICS")
        print("─" * 60)
        print()
        print("  tddl --doctor")
        print(
            "      Read-only health check. Lists every required tool and\n"
            "      reports where Unity/Fil-C resolve to. Installs nothing.\n"
            "      Exit code 0 if everything is ready, 1 otherwise.\n"
        )

        print("RUNNING TESTS")
        print("─" * 60)
        print()
        print("  tddl <test_file.c> [flags...]")
        print(
            "      Compiles and runs the test file. Looked up at:\n"
            "        ./tests/<stem>/<test_file.c>\n"
            "      where <stem> is <test_file.c> without the .c extension.\n"
            "\n"
            "      Unity is resolved in this order:\n"
            "        1. $UNITY_PATH (if set) — escape hatch for shared installs.\n"
            "        2. ./vendor/unity/  — populated by `tddl --build`.\n"
        )

        print("  Flags:")
        print()
        print("    --src <file.c>")
        print(
            "        Link an extra source file from src/ into the test build.\n"
            "        Required when the test exercises code that lives in src/.\n"
        )
        print("    --include <files>")
        print(
            "        Comma-separated list of header/source files from include/\n"
            "        to add to the build. e.g. --include mocks.c,helpers.c\n"
        )
        print("    --coverage")
        print(
            "        Run gcovr after the tests. Reports line coverage and\n"
            "        writes an HTML report to coverage/<stem>/index.html.\n"
            "        When combined with --src, coverage is filtered to that\n"
            "        file only (tests themselves are ignored).\n"
            "        Coverage below 100% causes tddl to exit non-zero.\n"
        )
        print("    --valgrind")
        print(
            "        Run the test binary under valgrind with strict memory\n"
            "        checks (--leak-check=full --show-leak-kinds=all\n"
            "        --track-origins=yes --error-exitcode=1).\n"
            "        Cannot be combined with --filc.\n"
        )
        print("    --filc")
        print(
            "        Compile with Fil-C, a memory-safe C compiler. Resolved\n"
            "        from $FIL_C_PATH or ./vendor/filc/build/bin/clang.\n"
            "        Build Fil-C first with `tddl --build-filc`.\n"
            "        Cannot be combined with --valgrind or --coverage.\n"
        )
        print("    --lizard [--ccn=N] [--length=N] [--args=N]")
        print(
            "        Run lizard static analysis on the test file (and on the\n"
            "        --src file, if passed). Any violation causes tddl to\n"
            "        exit non-zero.\n"
            f"        Default thresholds: CCN ≤ {DEFAULT_LIZARD_CCN}, "
            f"length ≤ {DEFAULT_LIZARD_LENGTH}, args ≤ {DEFAULT_LIZARD_ARGS}.\n"
            "        Override individually:\n"
            "            --ccn=N      max cyclomatic complexity per function\n"
            "            --length=N   max lines per function\n"
            "            --args=N     max parameters per function\n"
        )
        print("    --pdf")
        print(
            "        Generate a combined PDF report containing the Unity\n"
            "        test results, valgrind diagnostics, and lizard findings\n"
            "        (whichever of those ran). The terminal shows a short\n"
            "        summary; full output is captured into the PDF.\n"
            "        Written to: reports/<stem>/report.pdf\n"
        )

        print("EXAMPLES")
        print("─" * 60)
        print()
        print(
            "  # First-time setup\n"
            "  tddl --build\n"
            "\n"
            "  # Verify the environment is ready\n"
            "  tddl --doctor\n"
            "\n"
            "  # Basic test run\n"
            "  tddl test_list.c\n"
            "\n"
            "  # Test against the implementation in src/list.c, with coverage\n"
            "  tddl test_list.c --src list.c --coverage\n"
            "\n"
            "  # Full report: tests under valgrind, complexity check, PDF output\n"
            "  tddl test_list.c --src list.c --valgrind --lizard --pdf\n"
        )
        sys.exit(0)
       
    filename     = args[0]
    use_filc     = "--filc"     in args
    use_coverage = "--coverage" in args
    use_valgrind = "--valgrind" in args
    use_lizard   = "--lizard"   in args
    use_pdf      = "--pdf"      in args

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

    # `tddl --build`, `tddl --build-filc` e `tddl --doctor` são modos de
    # setup/diagnóstico, mutuamente exclusivos com qualquer execução de
    # teste. Checados em __main__.py.
    build_structure = args[0] == "--build"
    build_filc      = args[0] == "--build-filc"
    run_doctor_flag = args[0] == "--doctor"

    include_files = []

    if "--include" in args:
        idx = args.index("--include")

        if idx + 1 >= len(args):
            die(
                "--include requires a comma-separated list of filenames.\n"
                "  e.g. --include mocks.c,helpers.c\n"
                "  Files are looked up under include/."
            )

        include_arg = args[idx + 1]

        include_files = []

        for f in include_arg.split(","):
            if f.strip():
                include_files.append(f.strip())

    return (filename, use_filc, use_coverage, use_valgrind, use_lizard,
            ccn, length, args_, src_file, build_structure, include_files,
            use_pdf, build_filc, run_doctor_flag)