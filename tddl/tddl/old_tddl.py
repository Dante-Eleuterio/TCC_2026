#!/usr/bin/env python3
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
        ├── src/          <- reserved for future use
        └── tests/
            ├── test_constroi_nome.c   <- user-created test file
            └── CMakeLists.txt         <- generated once by tddl
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path


# ============================================================================
#  Helpers
# ============================================================================

def die(message: str, code: int = 1) -> None:
    print(f"[tddl] ERROR: {message}", file=sys.stderr)
    sys.exit(code)


def info(message: str) -> None:
    print(f"[tddl] {message}")


# ============================================================================
#  Environment validation
# ============================================================================

def get_unity_path() -> Path:
    raw = os.environ.get("UNITY_PATH")
    if not raw:
        die(
            "UNITY_PATH is not set.\n"
            "  Add the following line to your ~/.bashrc or ~/.zshrc:\n"
            "      export UNITY_PATH=\"/path/to/Unity\"\n"
            "  Then run:  source ~/.bashrc"
        )
    unity = Path(raw)
    if not unity.is_dir():
        die(f"UNITY_PATH points to a non-existent directory: {unity}")
    if not (unity / "src" / "unity.c").exists():
        die(f"Could not find unity.c inside UNITY_PATH/src: {unity / 'src' / 'unity.c'}")
    return unity

def get_filc_path() -> Path:
    raw = os.environ.get("FIL_C_PATH")
    if not raw:
        die(
            "FIL_C_PATH is not set.\n"
            "  Add the following line to your ~/.bashrc or ~/.zshrc:\n"
            "      export FIL_C_PATH=\"/path/to/fil-c/build/llvm-project/build/bin/clang\"\n"
            "  Then run:  source ~/.bashrc"
        )
    filc = Path(raw)
    if not filc.is_file():
        die(f"FIL_C_PATH points to a non-existent file: {filc}")
    return filc

def check_tools(use_filc,use_coverage) -> None:
    tools = ["cmake"]
    if use_coverage:
        tools.append("gcovr")
    for tool in tools:
        if not shutil.which(tool):
            die(f"Required tool not found in PATH: {tool}")


# ============================================================================
#  Path resolution
# ============================================================================

def get_root() -> Path: 
    return Path.cwd()


def resolve_paths(arg: str) -> tuple[Path, Path, Path]:
    """
    Given just a filename like 'test_constroi_nome.c', resolve:
        root      = cwd()                             e.g. /home/user/project
        tests_dir = cwd()/tests/                      e.g. /home/user/project/tests
        test_file = cwd()/tests/test_constroi_name/test_constroi_nome.c

    Dies if:
        - the argument is not a .c file
        - cwd()/tests/ does not exist
        - the resolved test file does not exist
    """
    # Strip any path the user may have accidentally included — we only want the filename
    filename = Path(arg).name

    if not filename.endswith(".c"):
        die(f"Expected a .c filename, got: {arg}")

    root = get_root()
    all_tests_dir = root / "tests"
    stem      = Path(filename).stem 
    test_dir  = all_tests_dir/stem
    test_file = test_dir/filename

    if not all_tests_dir.is_dir():
        die(
            f"tests/ directory not found in: {root}\n"
            f"  Make sure you are running tddl from the project root and the project is built"
        )

    if not test_file.exists():
        die(
            f"Test file not found: {test_file}\n"
            f"  Please create it manually with your Unity tests inside #ifdef TEST."
        )

    return root, test_dir, test_file


def ensure_structure(root: Path) -> None:
    """Create include/, src/, tests/ if they don't exist. List all created dirs."""
    dirs = {
        "include": root / "include",
        "src":     root / "src",
        "tests":   root / "tests",
    }
    created = []
    for name, path in dirs.items():
        if not path.exists():
            path.mkdir(parents=True)
            created.append(path)

    if created:
        info("Created the following directories:")
        for path in created:
            info(f"  {path}")
    else:
        info("Project structure already exists — no directories created.")


# ============================================================================
#  CMakeLists.txt generation (tests/ only, created once)
# ============================================================================

def generate_cmakelists(
    root:      Path,
    test_dir:  Path,
    test_file: Path,
    unity:     Path,
    use_coverage: bool,
    use_filc:  bool,
    filc:      Path | None,
) -> None:
    """
    Create tests/<stem>/CMakeLists.txt only if it does not already exist.
    Standalone — builds independently with no root CMakeLists.txt.
    In --filc mode: sets CMAKE_C_COMPILER to Fil-C and omits coverage flags.
    """
    cmake_path = test_dir / "CMakeLists.txt"

    if cmake_path.exists():
        info("tests/CMakeLists.txt already exists — skipping generation.")
        return

    project   = root.name
    target    = f"tddl_{test_file.stem}"
    unity_src = unity / "src" / "unity.c"
    unity_inc = unity / "src"
    inc_dir   = root / "include"

    # Compiler block — only injected in --filc mode
    compiler_block = (
        f"set(CMAKE_C_COMPILER {filc})\n\n"
        if use_filc else ""
    )

    # Coverage flags — only in normal mode
    if use_coverage:
        compile_options_block = (
            f"target_compile_options({target} PRIVATE\n"
            f"    --coverage\n"
            f"    -O0\n"
            f"    -g\n"
            f")\n\n"
        )
        link_options_block = (
            f"target_link_options({target} PRIVATE\n"
            f"    --coverage\n"
            f")\n"
        )
    else:
        compile_options_block = ""
        link_options_block    = ""

    if use_filc:
        mode_comment = "# Mode: Fil-C (memory-safe, no coverage)"
    elif use_coverage:
        mode_comment = "# Mode: gcc (coverage enabled via gcovr)"
    else:
        mode_comment = "# Mode: gcc (no coverage)"

    cmake_content = f"""\
cmake_minimum_required(VERSION 3.10)
{compiler_block}project({project}_tests C)

set(CMAKE_C_STANDARD 11)

{mode_comment}

# ============================================================================
#  Directories
# ============================================================================

set(INC_DIR   {inc_dir})
set(UNITY_INC {unity_inc})

# ============================================================================
#  Test target : {target}
#  Test file   : {test_file.name}
# ============================================================================

add_executable({target}
    {test_file}
    {unity_src}
)

target_include_directories({target} PRIVATE
    ${{INC_DIR}}
    ${{UNITY_INC}}
)

target_compile_definitions({target} PRIVATE
    TEST
)

{compile_options_block}{link_options_block}"""

    cmake_path.write_text(cmake_content)
    info(f"Generated CMakeLists.txt at: {cmake_path}")


# ============================================================================
#  Build & run
# ============================================================================

def cmake_configure(tests_dir: Path, build_dir: Path) -> None:
    info("Configuring with CMake...")
    result = subprocess.run(
        ["cmake", "-S", str(tests_dir), "-B", str(build_dir), "-DCMAKE_BUILD_TYPE=Debug"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        die("CMake configuration failed.")


def cmake_build(build_dir: Path, target: str) -> None:
    info(f"Building target '{target}'...")
    result = subprocess.run(
        ["cmake", "--build", str(build_dir), "--target", target],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        die("Build failed.")


def run_tests(build_dir: Path, target: str) -> bool:
    executable = build_dir / target
    if not executable.exists():
        candidates = list(build_dir.rglob(target))
        if not candidates:
            die(f"Test executable not found after build: {target}")
        executable = candidates[0]

    info(f"Running tests: {executable}")
    print()
    result = subprocess.run([str(executable)])
    print()
    return result.returncode == 0


def run_gcovr(root: Path, build_dir: Path, test_file: Path, test_dir: Path) -> None:
    coverages_dir = root / "coverage"
    coverages_dir.mkdir(exist_ok=True)
    test_coverage_dir = coverages_dir / test_dir.name
    if test_coverage_dir.exists():
        print("batata 2\n")
        #shutil.rmtree(test_coverage_dir)  # deletes everything inside
    test_coverage_dir.mkdir(exist_ok=True)

    html_output = test_coverage_dir / "index.html"

    info("Running gcovr...")
    print()

    # Terminal summary
    subprocess.run([
        "gcovr",
        "--root", str(root),
        "--filter", str(test_file),
        str(build_dir),
    ])

    # HTML report
    subprocess.run([
        "gcovr",
        "--root", str(root),
        "--filter", str(test_file),
        "--html", "--html-details",
        "-o", str(html_output),
        str(build_dir),
    ])

    print()
    info(f"HTML coverage report saved to: {html_output}")


# ============================================================================
#  Cleanup
# ============================================================================

def cleanup(build_dir: Path) -> None:
    info("Cleaning up build directory...")
    shutil.rmtree(build_dir, ignore_errors=True)


# ============================================================================
#  Function Arguments
# ============================================================================

def parse_args() -> tuple[str, bool, bool]:
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
        print(
            "  Expected structure:\n"
            "    project/        <- run tddl from here\n"
            "    ├── include/    <- public headers (.h)\n"
            "    ├── src/        <- reserved for future use\n"
            "    └── tests/\n"
            "        └── test01/\n"
            "            └── test01.c\n"   
            "            └── CMakeLists.txt <- optional, if not exists then tddl will create one\n"   
        )
        print("Usage: $tddl <test_file.c> --coverage")
        print("  -Expects same project structure as in normal usage\n")
        print("  -Runs all tests and then uses gcovr for coverage tests \n")
        print("  -Creates project/coverage folder \n")

        print("Usage: $tddl <test_file.c> --filc")
        print("  -Expects same project structure as in normal usage\n")
        print("  -Compiles test with filc and then runs all tests \n")
        sys.exit(0)

    if len(args) > 2:
        die("Too many arguments. Usage: tddl <test_file.c> [--filc or --coverage]")

    filename = args[0]
    use_filc = "--filc" in args
    use_coverage = "--coverage" in args

    return filename, use_filc, use_coverage

    
# ============================================================================
#  Main
# ============================================================================

def main() -> None:
    filename, use_filc, use_coverage = parse_args()

    check_tools(use_filc,use_coverage)
    filc  = get_filc_path() if use_filc else None

    unity                       = get_unity_path()
    root, test_dir, test_file   = resolve_paths(filename)
    ensure_structure(root)
    target                      = f"tddl_{test_file.stem}"

    build_dir = Path(tempfile.mkdtemp(prefix="tddl_build_"))

    info(f"Project  : {root}")
    info(f"Test file: {test_file}")
    info(f"Unity    : {unity}")
    info(f"Target   : {target}")
    info(f"Mode     : {'Fil-C (memory-safe)' if use_filc else 'gcc (coverage)'}")
    info(f"Build    : {build_dir}")
    print()

    generate_cmakelists(root, test_dir, test_file, unity,use_coverage, use_filc, filc)

    tests_passed = False
    try:
        cmake_configure(test_dir, build_dir)
        cmake_build(build_dir, target)
        tests_passed = run_tests(build_dir, target)

        if use_coverage:
            if not tests_passed:
                info("Tests FAILED — skipping gcovr.")
            else:
                run_gcovr(root, build_dir, test_file,test_dir)
        elif not tests_passed:
            info("Tests FAILED ")

    finally:
        cleanup(build_dir)

    sys.exit(0 if tests_passed else 1)


if __name__ == "__main__":
    main()
