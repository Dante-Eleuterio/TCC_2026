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
import os
from pathlib import Path
import shutil

from .helpers import *

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

def check_tools(use_coverage: bool, use_valgrind: bool = False) -> None:
    tools = ["cmake"]
    if use_coverage:
        tools.append("gcovr")
    if use_valgrind:
        tools.append("valgrind")
    for tool in tools:
        if not shutil.which(tool):
            die(f"Required tool not found in PATH: {tool}")