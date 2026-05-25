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
import subprocess
from pathlib import Path
from .helpers import *


# ============================================================================
#  CMakeLists.txt generation (tests/ only, created once)
# ============================================================================

def generate_cmakelists(
    root:         Path,
    test_dir:     Path,
    test_file:    Path,
    unity:        Path,
    use_coverage: bool,
    use_filc:     bool,
    filc:         Path | None,
    src_file:     Path | None = None,
    wrap_funcs:   list[str]   = [],
    include_list: list[str]   = []
) -> None:
    cmake_path = test_dir / "CMakeLists.txt"

    if cmake_path.exists():
        info(f"Deleting {cmake_path}")
        cmake_path.unlink()

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

    extra_sources = ""

    if src_file:
        extra_sources += f"    {src_file}\n"

    extra_sources += "".join(
        f"    {inc}\n"
        for inc in include_list
    )

    # Coverage flags — only when --coverage is passed
    if use_coverage:
        compile_options_block = (
            f"target_compile_options({target} PRIVATE\n"
            f"    --coverage\n"
            f"    -O0\n"
            f"    -g\n"
            f")\n\n"
        )
        coverage_link_flags = "    --coverage\n"
    else:
        compile_options_block = ""
        coverage_link_flags   = ""

    # --wrap flags — one per function
    wrap_link_flags = "".join(
        f"    -Wl,--wrap={fn}\n" for fn in wrap_funcs
    )

    # Combine coverage + wrap into a single target_link_options block
    all_link_flags = coverage_link_flags + wrap_link_flags
    link_options_block = (
        f"target_link_options({target} PRIVATE\n"
        f"{all_link_flags}"
        f")\n"
    ) if all_link_flags else ""

    if use_filc:
        mode_comment = "# Mode: Fil-C (memory-safe, no coverage)"
    elif use_coverage:
        mode_comment = "# Mode: gcc (coverage enabled via gcovr)"
    else:
        mode_comment = "# Mode: gcc (no coverage)"

    src_comment = (
        f"#  Src file    : {src_file.name} (linked separately)\n"
        if src_file else
        "#  Src file    : embedded in test file\n"
    )

    wrap_comment = (
        f"#  Wrapped     : {', '.join(wrap_funcs)}\n"
        if wrap_funcs else ""
    )

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
{src_comment}{wrap_comment}# ============================================================================

add_executable({target}
    {test_file}
    {unity_src}
{extra_sources})

target_include_directories({target} PRIVATE
    ${{INC_DIR}}
    ${{UNITY_INC}}
)

target_compile_definitions({target} PRIVATE
    TEST
    UNITY_USE_COMMAND_LINE_ARGS
    UNITY_OUTPUT_COLOR
)

{compile_options_block}{link_options_block}"""

    cmake_path.write_text(cmake_content)
    info(f"Generated CMakeLists.txt at: {cmake_path}")


# ============================================================================
#  Build
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