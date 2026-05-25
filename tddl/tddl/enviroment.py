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
Resolução de paths externos (Unity, Fil-C) e checagem de ferramentas.

Estratégia de resolução (em ordem):
  1. Variável de ambiente (UNITY_PATH / FIL_C_PATH) — override explícito.
  2. ./vendor/ no projeto — local-padrão depois de `tddl --build`.
  3. Erro com hint pra rodar `tddl --build`.

Isso permite:
  - "just works" depois do `tddl --build` sem env vars.
  - reaproveitar uma instalação global via export se quiser.
"""
import os
from pathlib import Path
import shutil

from .helpers import die, info


def _vendor_unity(root: Path) -> Path:
    return root / "vendor" / "unity"


def _vendor_filc_clang(root: Path) -> Path:
    return root / "vendor" / "filc" / "build" / "bin" / "clang"


def get_unity_path(root: Path | None = None) -> Path:
    """
    Resolve onde está o Unity, na seguinte ordem:
      1. $UNITY_PATH (se definido e válido)
      2. ./vendor/unity (se existir e tiver src/unity.c)
      3. erro — instrui a rodar `tddl --build`

    O parâmetro root vem do __main__ (Path.cwd()) pra evitar acoplar
    esse módulo ao path.get_root().
    """
    if root is None:
        root = Path.cwd()

    # 1) Env var como override
    raw = os.environ.get("UNITY_PATH")
    if raw:
        unity = Path(raw)
        if not unity.is_dir():
            die(
                f"UNITY_PATH is set but points to a non-existent directory:\n"
                f"  {unity}\n"
                f"  Either fix the path, or `unset UNITY_PATH` to fall back\n"
                f"  to the vendored Unity at {_vendor_unity(root)}."
            )
        if not (unity / "src" / "unity.c").exists():
            die(
                f"UNITY_PATH is set but doesn't look like a Unity checkout:\n"
                f"  Expected: {unity / 'src' / 'unity.c'}\n"
                f"  Either fix the path, or `unset UNITY_PATH` to fall back\n"
                f"  to the vendored Unity at {_vendor_unity(root)}."
            )
        return unity

    # 2) Vendor dir do projeto
    vendored = _vendor_unity(root)
    if (vendored / "src" / "unity.c").exists():
        return vendored

    # 3) Não achou — hint claro
    die(
        "Unity not found.\n"
        f"  Looked at: {vendored}\n"
        "  Run `tddl --build` from the project root to install Unity automatically,\n"
        "  or set UNITY_PATH=/path/to/Unity to use an existing installation."
    )


def get_filc_path(root: Path | None = None) -> Path:
    """
    Resolve onde está o clang do Fil-C, na seguinte ordem:
      1. $FIL_C_PATH (se definido e válido)
      2. ./vendor/filc/build/bin/clang
      3. erro — instrui a rodar `tddl --build-filc`
    """
    if root is None:
        root = Path.cwd()

    # 1) Env var como override
    raw = os.environ.get("FIL_C_PATH")
    if raw:
        filc = Path(raw)
        if not filc.is_file():
            die(
                f"FIL_C_PATH is set but points to a non-existent file:\n"
                f"  {filc}\n"
                f"  Either fix the path, or `unset FIL_C_PATH` to fall back\n"
                f"  to the vendored Fil-C at {_vendor_filc_clang(root)}."
            )
        return filc

    # 2) Vendor dir do projeto
    vendored = _vendor_filc_clang(root)
    if vendored.is_file():
        return vendored

    # 3) Não achou
    die(
        "Fil-C clang binary not found.\n"
        f"  Looked at: {vendored}\n"
        "  Run `tddl --build-filc` from the project root to build Fil-C automatically\n"
        "  (takes 30-60 minutes), or set FIL_C_PATH=/path/to/clang to use an\n"
        "  existing build."
    )


def check_tools(
    use_coverage: bool,
    use_valgrind: bool = False,
    use_lizard:   bool = False,
    use_pdf:      bool = False,
) -> None:
    """
    Verifica se as ferramentas externas necessárias estão no PATH.

    Quando uma falta, a mensagem identifica qual flag a requer (em casos
    onde a relação não é óbvia) e aponta pra `tddl --build` / `tddl
    --doctor`.
    """
    # Lista de pares (tool, flag-que-requer). cmake é sempre necessário.
    required: list[tuple[str, str | None]] = [("cmake", None)]
    if use_coverage:
        required.append(("gcovr",    "--coverage"))
    if use_valgrind:
        required.append(("valgrind", "--valgrind"))
    if use_lizard:
        required.append(("lizard",   "--lizard"))

    for tool, flag in required:
        if shutil.which(tool):
            continue
        reason = (f" (needed for {flag})" if flag else
                  " (always required to build tests)")
        die(
            f"Required tool not found in PATH: {tool}{reason}\n"
            f"  Run `tddl --build` to install missing dependencies,\n"
            f"  or `tddl --doctor` to see the full diagnostic."
        )

    if use_pdf:
        try:
            import reportlab  # noqa: F401
        except ImportError:
            die(
                "Python package 'reportlab' is required for --pdf but is not\n"
                "  importable. Run `tddl --build` to install it, or install\n"
                "  manually with: pip install --user reportlab"
            )