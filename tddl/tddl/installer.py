# BSD 2-Clause License
#
# Copyright (c) 2026, Dante Eleutério dos Santos
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
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from .helpers import die, info


# ----------------------------------------------------------------------------
#  Constantes
# ----------------------------------------------------------------------------

UNITY_REPO    = "https://github.com/ThrowTheSwitch/Unity.git"
UNITY_TAG     = "v2.6.0"   # release estável; pin pra builds reproduzíveis

FILC_REPO     = "https://github.com/pizlonator/llvm-project-deluge.git"
# Fil-C não tem tag oficial; usamos main. Quem quiser pinar pode editar aqui.

# Pacotes do sistema, por gerenciador. Mantemos nomes diferentes entre
# distros (ex.: build-essential vs base-devel) pra não exigir adivinhação.
SYSTEM_PACKAGES = {
    'apt': {
        'cmake':         ['cmake'],
        'valgrind':      ['valgrind'],
        'git':           ['git'],
        'build':         ['build-essential'],
        'pipx':          ['pipx'],
    },
    'dnf': {
        'cmake':         ['cmake'],
        'valgrind':      ['valgrind'],
        'git':           ['git'],
        'build':         ['gcc', 'gcc-c++', 'make'],
        'pipx':          ['pipx'],
    },
    'pacman': {
        'cmake':         ['cmake'],
        'valgrind':      ['valgrind'],
        'git':           ['git'],
        'build':         ['base-devel'],
        'pipx':          ['python-pipx'],
    },
    'brew': {
        'cmake':         ['cmake'],
        'valgrind':      [],   # valgrind não roda em macOS recente; alertamos
        'git':           ['git'],
        'build':         [],   # vem com Xcode CLT
        'pipx':          ['pipx'],
    },
}

# Ferramentas Python instaladas via pipx (não-sudo, isoladas).
PIPX_TOOLS = ['lizard', 'gcovr']

# reportlab é biblioteca, não CLI — fica via pip --user ou pipx inject.
PIP_LIBS = ['reportlab']


# ----------------------------------------------------------------------------
#  Detecção de OS / package manager
# ----------------------------------------------------------------------------

def detect_pkg_manager() -> str:
    """Retorna 'apt', 'dnf', 'pacman', 'brew', ou aborta com erro claro."""
    candidates = [
        ('apt',    'apt-get'),   # Debian/Ubuntu
        ('dnf',    'dnf'),       # Fedora/RHEL recente
        ('pacman', 'pacman'),    # Arch
        ('brew',   'brew'),      # macOS
    ]
    for name, binary in candidates:
        if shutil.which(binary):
            return name
    die(
        "Could not detect a supported package manager.\n"
        "  Supported: apt (Debian/Ubuntu), dnf (Fedora), pacman (Arch), brew (macOS).\n"
        "  Install dependencies manually (cmake, valgrind, git, lizard, gcovr, reportlab)\n"
        "  and then re-run `tddl --build`."
    )


def _macos_warn_valgrind() -> None:
    """macOS recente não tem valgrind funcional. Avisa em vez de tentar."""
    if platform.system() == 'Darwin':
        info("WARNING: valgrind is not supported on recent macOS (Apple Silicon)."
             " --valgrind will not work; use --filc for memory safety instead.")


# ----------------------------------------------------------------------------
#  Execução de comandos com feedback
# ----------------------------------------------------------------------------

def _run(cmd: list[str], description: str, check: bool = True) -> int:
    """Roda comando mostrando o que tá fazendo. Aborta se check e falhar."""
    info(f"→ {description}")
    info(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if check and result.returncode != 0:
        die(f"Command failed (exit {result.returncode}): {' '.join(cmd)}")
    return result.returncode


def _sudo_prefix() -> list[str]:
    """sudo só se não estivermos rodando como root."""
    if os.geteuid() == 0:
        return []
    if not shutil.which('sudo'):
        die("Need root to install system packages, but `sudo` is not available.\n"
            "  Run as root or install sudo and re-try.")
    return ['sudo']


def _pm_install(pm: str, packages: list[str]) -> None:
    """Instala via package manager apropriado. Faz nada se lista vazia."""
    if not packages:
        return
    sudo = _sudo_prefix()
    if pm == 'apt':
        _run(sudo + ['apt-get', 'update'], "Refreshing apt index")
        _run(sudo + ['apt-get', 'install', '-y', *packages],
             f"Installing system packages: {', '.join(packages)}")
    elif pm == 'dnf':
        _run(sudo + ['dnf', 'install', '-y', *packages],
             f"Installing system packages: {', '.join(packages)}")
    elif pm == 'pacman':
        _run(sudo + ['pacman', '-S', '--noconfirm', *packages],
             f"Installing system packages: {', '.join(packages)}")
    elif pm == 'brew':
        # brew não usa sudo
        _run(['brew', 'install', *packages],
             f"Installing packages via brew: {', '.join(packages)}")
    else:
        die(f"Internal error: unsupported package manager {pm}")


# ----------------------------------------------------------------------------
#  Instalação de tools
# ----------------------------------------------------------------------------

def _ensure_system_tools(pm: str) -> None:
    """
    Instala cmake, valgrind, git e build-essential se faltando.
    Pula tools já instaladas (idempotente).
    """
    spec = SYSTEM_PACKAGES[pm]
    to_install: list[str] = []

    # cmake/git/valgrind: chave 1-pra-1 com o binário no PATH
    checks = [('cmake', 'cmake'), ('git', 'git'), ('valgrind', 'valgrind')]
    for tool, binary in checks:
        if shutil.which(binary):
            info(f"✓ {tool} already installed ({shutil.which(binary)})")
        else:
            if tool == 'valgrind' and pm == 'brew':
                _macos_warn_valgrind()
                continue
            to_install.extend(spec[tool])

    # build-essential / equivalente — checa pela presença do gcc
    if shutil.which('gcc') or shutil.which('cc'):
        info("✓ C compiler already installed")
    else:
        to_install.extend(spec['build'])

    # pipx — necessário pra lizard/gcovr/reportlab
    if shutil.which('pipx'):
        info(f"✓ pipx already installed ({shutil.which('pipx')})")
    else:
        to_install.extend(spec['pipx'])

    _pm_install(pm, to_install)

    # Garante que ~/.local/bin (target do pipx) está no PATH pra esta sessão
    # e pras futuras (ensurepath atualiza ~/.bashrc/~/.zshrc).
    if shutil.which('pipx'):
        _run(['pipx', 'ensurepath'], "Ensuring pipx PATH is configured",
             check=False)


def _ensure_python_tools() -> None:
    """Instala lizard, gcovr, reportlab via pipx (isolados, no PATH)."""
    if not shutil.which('pipx'):
        die("pipx not found after system install — aborting.")

    for tool in PIPX_TOOLS:
        if shutil.which(tool):
            info(f"✓ {tool} already installed ({shutil.which(tool)})")
            continue
        _run(['pipx', 'install', tool],
             f"Installing Python tool: {tool}", check=False)

    try:
        import reportlab  # noqa: F401
        info("✓ reportlab already importable")
    except ImportError:
        # Tenta pip --user primeiro (mais leve), com fallback --break-system-packages
        info("→ Installing reportlab for Python (used by --pdf)")
        rc = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--user', 'reportlab'],
        ).returncode
        if rc != 0:
            info("  pip --user failed, retrying with --break-system-packages")
            _run(
                [sys.executable, '-m', 'pip', 'install',
                 '--user', '--break-system-packages', 'reportlab'],
                "Installing reportlab (fallback)", check=False,
            )


# ----------------------------------------------------------------------------
#  Vendoring (Unity, Fil-C)
# ----------------------------------------------------------------------------

def vendor_dir(root: Path) -> Path:
    return root / 'vendor'


def unity_vendor_dir(root: Path) -> Path:
    return vendor_dir(root) / 'unity'


def filc_vendor_dir(root: Path) -> Path:
    return vendor_dir(root) / 'filc'


def filc_clang_path(root: Path) -> Path:
    """Onde o binário do clang do Fil-C fica depois de buildado."""
    return filc_vendor_dir(root) / 'build' / 'bin' / 'clang'


def _ensure_unity(root: Path) -> None:
    """
    Clona Unity em ./vendor/unity/ se ainda não existir.
    Idempotente: se já existir um clone válido, pula.
    """
    target = unity_vendor_dir(root)
    marker = target / 'src' / 'unity.c'   # mesmo arquivo que enviroment.py valida

    if marker.exists():
        info(f"✓ Unity already vendored at {target}")
        return

    if target.exists():
        info(f"Removing incomplete Unity directory at {target}")
        shutil.rmtree(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    _run(
        ['git', 'clone', '--depth', '1', '--branch', UNITY_TAG,
         UNITY_REPO, str(target)],
        f"Cloning Unity {UNITY_TAG} into {target}",
    )

    if not marker.exists():
        die(f"Unity clone finished but {marker} not found — clone may be corrupt.")


def _ensure_filc(root: Path) -> None:
    """
    Clona e compila Fil-C. Demora 30-60 min e ocupa vários GB.
    Só chamado por --build-filc, nunca por --build.
    """
    target = filc_vendor_dir(root)
    clang  = filc_clang_path(root)

    if clang.exists():
        info(f"✓ Fil-C already built at {clang}")
        return

    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        _run(
            ['git', 'clone', '--depth', '1', FILC_REPO, str(target)],
            f"Cloning Fil-C into {target} (this is several GB)",
        )
    else:
        info(f"Fil-C source already at {target}, skipping clone")

    # Fil-C tem um setup_filc.sh que cuida do build. Se mudarem o nome
    # no upstream, esse passo precisa ser revisitado.
    setup_script = target / 'setup_filc.sh'
    if not setup_script.exists():
        die(
            f"Fil-C build script not found: {setup_script}\n"
            f"  Upstream layout may have changed. Build Fil-C manually and place\n"
            f"  the resulting clang at: {clang}"
        )

    info("→ Building Fil-C (this will take 30-60 minutes and ~10-20 GB of disk)")
    info("  Output will be shown live below.")
    _run(
        ['bash', str(setup_script)],
        f"Running {setup_script.name}",
    )

    if not clang.exists():
        die(
            f"Fil-C build finished but clang binary not found at {clang}.\n"
            f"  Inspect the build output above for errors."
        )
    info(f"✓ Fil-C built successfully at {clang}")


# ----------------------------------------------------------------------------
#  .gitignore management
# ----------------------------------------------------------------------------

_GITIGNORE_MARK = "# >>> tddl-managed >>>"
_GITIGNORE_END  = "# <<< tddl-managed <<<"
_GITIGNORE_BODY = "\n".join([
    _GITIGNORE_MARK,
    "vendor/",
    "reports/",
    "coverage/",
    _GITIGNORE_END,
])


def _ensure_gitignore(root: Path) -> None:
    """
    Garante que ./gitignore tem um bloco gerenciado pelo tddl ignorando
    vendor/, reports/ e coverage/. Não toca em outras regras.
    """
    gi = root / '.gitignore'
    existing = gi.read_text() if gi.exists() else ''

    if _GITIGNORE_MARK in existing:
        info("✓ .gitignore already has tddl-managed block")
        return

    new = existing
    if new and not new.endswith('\n'):
        new += '\n'
    if new:
        new += '\n'
    new += _GITIGNORE_BODY + '\n'

    gi.write_text(new)
    info(f"Added tddl-managed block to {gi}")


# ----------------------------------------------------------------------------
#  Entry points (chamados por __main__.py)
# ----------------------------------------------------------------------------

def run_build(root: Path) -> None:
    """
    Executa o `tddl --build`:
      - cria estrutura de pastas (include/src/tests/) se faltando
      - detecta package manager
      - instala system tools (cmake, valgrind, git, gcc)
      - instala python tools (lizard, gcovr, reportlab)
      - clona Unity em ./vendor/unity/
      - atualiza .gitignore
    """
    info("=" * 60)
    info("tddl --build — installing dependencies and bootstrapping project")
    info("=" * 60)

    pm = detect_pkg_manager()
    info(f"Detected package manager: {pm}")
    _macos_warn_valgrind()
    print()

    info("─── 1/4: System tools ──────────────────────────────")
    _ensure_system_tools(pm)
    print()

    info("─── 2/4: Python tools ──────────────────────────────")
    _ensure_python_tools()
    print()

    info("─── 3/4: Unity (vendored) ──────────────────────────")
    _ensure_unity(root)
    print()

    info("─── 4/4: Project layout ────────────────────────────")
    # create_structure() vive em path.py; importamos aqui pra evitar ciclo.
    from .path import create_structure
    create_structure(root)
    _ensure_gitignore(root)
    print()

    info("=" * 60)
    info("Build complete. You can now run:")
    info(f"  tddl <test_file.c>")
    info("")
    info("To install Fil-C (optional, ~30-60 min build), run:")
    info(f"  tddl --build-filc")
    info("=" * 60)


def run_build_filc(root: Path) -> None:
    """
    Executa o `tddl --build-filc`: instala Fil-C separadamente.
    Não roda `--build` antes; assume que git/build-essential já estão lá.
    """
    info("=" * 60)
    info("tddl --build-filc — building Fil-C (this takes 30-60 minutes)")
    info("=" * 60)

    # Sanidade: precisa de git e compiler. Se o usuário pulou --build,
    # damos uma mensagem útil em vez de quebrar no meio do clone.
    missing = [t for t in ('git', 'cmake')
               if not shutil.which(t)]
    if not (shutil.which('gcc') or shutil.which('cc')):
        missing.append('gcc')
    if missing:
        die(
            f"Missing prerequisites for Fil-C build: {', '.join(missing)}\n"
            "  Run `tddl --build` first to install base dependencies."
        )

    _ensure_filc(root)
    print()
    info("=" * 60)
    info(f"Fil-C built at: {filc_clang_path(root)}")
    info("You can now use `tddl <test_file.c> --filc`")
    info("=" * 60)


# ----------------------------------------------------------------------------
#  Doctor: read-only health check
# ----------------------------------------------------------------------------

def _supports_color() -> bool:
    return sys.stdout.isatty()


def _sym(kind: str) -> str:
    table_color = {
        'ok':    '\033[32m✓\033[0m',   # verde
        'miss':  '\033[31m✗\033[0m',   # vermelho
        'warn':  '\033[33m⚠\033[0m',   # amarelo
        'info':  '\033[36mi\033[0m',   # ciano
    }
    table_plain = {'ok': 'OK', 'miss': 'MISSING', 'warn': 'WARN', 'info': 'INFO'}
    return (table_color if _supports_color() else table_plain)[kind]


def _doctor_row(label: str, status: str, detail: str = '') -> None:
    """Imprime uma linha do relatório: símbolo + label + detalhe."""
    sym = _sym(status)
    label_padded = label.ljust(20)
    if detail:
        print(f"  {sym}  {label_padded} {detail}")
    else:
        print(f"  {sym}  {label_padded}")


def _check_binary(name: str, *, required: bool = True) -> bool:
    """Verifica binário no PATH. Retorna True se encontrado."""
    path = shutil.which(name)
    if path:
        _doctor_row(name, 'ok', path)
        return True
    _doctor_row(name, 'miss' if required else 'warn',
                'not found in PATH' + ('' if required else ' (optional)'))
    return False


def _check_python_lib(name: str, *, required: bool = True) -> bool:
    """Tenta importar lib Python. Retorna True se importou."""
    try:
        mod = __import__(name)
    except ImportError:
        _doctor_row(name, 'miss' if required else 'warn',
                    'cannot import' + ('' if required else ' (optional)'))
        return False
    version = getattr(mod, '__version__', '?')
    _doctor_row(name, 'ok', f'v{version}')
    return True


def _check_unity(root: Path) -> bool:
    """
    Verifica em ordem:
      1. $UNITY_PATH (se setado)
      2. ./vendor/unity/
    Sucesso se uma das duas resolve pra um Unity válido.
    """
    env = os.environ.get('UNITY_PATH')
    if env:
        p = Path(env)
        if (p / 'src' / 'unity.c').exists():
            _doctor_row('Unity', 'ok', f'{p} (via $UNITY_PATH)')
            return True
        else:
            _doctor_row('Unity', 'miss',
                        f'$UNITY_PATH={env} but src/unity.c not found there')
            return False

    vendored = unity_vendor_dir(root)
    if (vendored / 'src' / 'unity.c').exists():
        _doctor_row('Unity', 'ok', f'{vendored} (vendored)')
        return True

    _doctor_row('Unity', 'miss',
                f'not at {vendored} and $UNITY_PATH not set')
    return False


def _check_filc(root: Path) -> bool:
    """
    Verifica em ordem: $FIL_C_PATH → ./vendor/filc/build/bin/clang.
    Opcional — só necessário pra `--filc`. Retorna True se encontrado.
    """
    env = os.environ.get('FIL_C_PATH')
    if env:
        if Path(env).is_file():
            _doctor_row('Fil-C', 'ok', f'{env} (via $FIL_C_PATH)')
            return True
        else:
            _doctor_row('Fil-C', 'miss', f'$FIL_C_PATH={env} but file missing')
            return False

    vendored = filc_clang_path(root)
    if vendored.is_file():
        _doctor_row('Fil-C', 'ok', f'{vendored} (vendored)')
        return True

    _doctor_row('Fil-C', 'warn',
                'not built (optional — run `tddl --build-filc` if you need --filc)')
    return False


def _check_pkg_manager() -> str | None:
    """Detecta pkg manager sem abortar (detect_pkg_manager dá die())."""
    for name, binary in [('apt', 'apt-get'), ('dnf', 'dnf'),
                         ('pacman', 'pacman'), ('brew', 'brew')]:
        if shutil.which(binary):
            _doctor_row('package manager', 'ok', f'{name} ({shutil.which(binary)})')
            return name
    _doctor_row('package manager', 'warn',
                'none of apt/dnf/pacman/brew detected — `tddl --build` will not work')
    return None


def run_doctor(root: Path) -> int:
    """
    Diagnóstico read-only do ambiente. Retorna o exit code:
      0 → tudo necessário pro fluxo principal (`tddl <file>`) está ok.
      1 → algo essencial está faltando.

    Considerações:
      - cmake/git/gcc/Unity são essenciais → faltando = exit 1
      - valgrind/lizard/gcovr/reportlab → necessários só pras flags
        correspondentes, mas listamos como "miss" porque normalmente
        o usuário quer todas as features. Falta deles também conta
        pra exit 1.
      - Fil-C é separado (--build-filc não roda automático), então
        falta dele é WARN, não MISSING. Não conta pro exit 1.
    """
    print()
    info("tddl --doctor — checking environment")
    info("=" * 60)
    print()

    print("System:")
    print(f"  platform: {platform.system()} {platform.release()} ({platform.machine()})")
    pm_name = _check_pkg_manager()
    print()

    print("Build toolchain:")
    have_cmake  = _check_binary('cmake')
    have_git    = _check_binary('git')
    have_gcc    = _check_binary('gcc') or _check_binary('cc')
    # gcc OU cc é o que importa, então se gcc faltou mas cc tá lá, ok.
    # _check_binary já imprimiu as duas linhas — bom o suficiente pra
    # diagnóstico.
    print()

    print("Testing & analysis tools:")
    have_valgrind = _check_binary('valgrind')
    have_lizard   = _check_binary('lizard')
    have_gcovr    = _check_binary('gcovr')
    have_pipx     = _check_binary('pipx', required=False)
    print()

    print("Python libraries:")
    have_reportlab = _check_python_lib('reportlab')
    print()

    print("Project dependencies (resolved against current directory):")
    print(f"  project root: {root}")
    have_unity = _check_unity(root)
    _check_filc(root)   # Fil-C não bloqueia, ignoramos retorno
    print()

    print("Project structure:")
    for d in ('include', 'src', 'tests'):
        if (root / d).is_dir():
            _doctor_row(f'{d}/', 'ok', str(root / d))
        else:
            _doctor_row(f'{d}/', 'warn',
                        f'not present (run `tddl --build` to create)')
    print()

    # Resumo: o que é essencial pro fluxo `tddl <file>` mínimo:
    #   cmake + gcc/cc + Unity → tests compilam e rodam.
    # Tudo o resto é por-flag (valgrind só pra --valgrind, etc).
    # Pra um diagnóstico útil, marcamos faltas em qualquer tool de teste
    # como problema, porque o usuário normalmente quer tudo.
    essential_missing = []
    if not have_cmake:    essential_missing.append('cmake')
    if not have_gcc:      essential_missing.append('gcc')
    if not have_unity:    essential_missing.append('Unity')

    optional_missing = []
    if not have_git:       optional_missing.append('git (needed by --build)')
    if not have_valgrind:  optional_missing.append('valgrind (for --valgrind)')
    if not have_lizard:    optional_missing.append('lizard (for --lizard)')
    if not have_gcovr:     optional_missing.append('gcovr (for --coverage)')
    if not have_reportlab: optional_missing.append('reportlab (for --pdf)')

    info("=" * 60)
    if essential_missing or optional_missing:
        info("Doctor summary:")
        if essential_missing:
            print(f"  {_sym('miss')} essential missing: {', '.join(essential_missing)}")
        if optional_missing:
            print(f"  {_sym('warn')} feature-specific missing: {', '.join(optional_missing)}")
        print()
        info("Run `tddl --build` to install missing dependencies.")
        info("(Fil-C is separate: run `tddl --build-filc` if you need --filc.)")
        # Exit 1 se algo essencial OU qualquer feature tool faltar — o
        # objetivo é o usuário ver "tudo verde" antes de considerar o
        # ambiente pronto.
        info("=" * 60)
        return 1

    info(f"{_sym('ok')} All checks passed. Environment is ready.")
    info("=" * 60)
    return 0