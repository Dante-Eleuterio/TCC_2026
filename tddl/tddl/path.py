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

from pathlib import Path
from .helpers import die, info
import re


def get_root() -> Path:
    return Path.cwd()


def resolve_paths(arg: str) -> tuple[Path, Path, Path]:
    """
    Estrutura esperada (achatada):
        project/
        ├── include/
        ├── src/
        └── tests/
            └── teste1.c   <- direto dentro de tests/

    Retorna:
        root      = cwd()
        test_dir  = cwd()/tests/      <- mesmo diretório para todos os testes
        test_file = cwd()/tests/<arg>
    """
    filename = Path(arg).name

    if not filename.endswith(".c"):
        die(f"Expected a .c filename, got: {arg}")

    root      = get_root()
    test_dir  = root / "tests"
    test_file = test_dir / filename

    if not test_dir.is_dir():
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


def resolve_src_file(root: Path, src_arg: str) -> Path:
    filename = Path(src_arg).name
    src_file = root / "src" / filename

    if not src_file.exists():
        die(
            f"Source file not found: {src_file}\n"
            f"  Make sure the file exists in <project>/src/"
        )

    return src_file


def ensure_structure(root: Path) -> None:
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


def extract_wrap_funcs(test_file: Path) -> list[str]:
    source = test_file.read_text()

    # matches: any return type, then __wrap_funcname, then (
    pattern = re.compile(r'\b__wrap_(\w+)\s*\(')
    matches = pattern.findall(source)

    # deduplicate while preserving order
    seen = set()
    wrap_funcs = []
    for fn in matches:
        if fn not in seen:
            seen.add(fn)
            wrap_funcs.append(fn)

    if wrap_funcs:
        info(f"Found wrapped functions: {', '.join(wrap_funcs)}")

    return wrap_funcs