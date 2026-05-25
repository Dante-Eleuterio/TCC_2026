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
Geração de relatório PDF unificado.

Estrutura geral:
  - dataclasses tipadas com os resultados de cada ferramenta (Unity, Lizard,
    futuramente Coverage e Valgrind)
  - parsers que convertem saída crua das ferramentas → dataclasses
  - geradores de seções (uma função por ferramenta) que produzem listas de
    Flowables do reportlab
  - generate_combined_pdf(): a única entry-point pública usada pelo
    __main__. Recebe as estruturas e monta o PDF inteiro numa página.

Quando uma ferramenta não foi executada, o caller passa None no lugar
do summary correspondente e a seção é simplesmente omitida.
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    CondPageBreak,
)


# ============================================================================
#  Paleta compartilhada
# ============================================================================

COLOR_PASS    = colors.HexColor('#1b7f3a')
COLOR_FAIL    = colors.HexColor('#c0392b')
COLOR_IGNORE  = colors.HexColor('#b58900')
COLOR_NEUTRAL = colors.HexColor('#2c3e50')
COLOR_MUTED   = colors.HexColor('#7f8c8d')
COLOR_BG_ROW  = colors.HexColor('#f4f6f7')
COLOR_HEADER  = colors.HexColor('#34495e')
COLOR_VIOL_BG = colors.HexColor('#fdedec')
COLOR_PASS_BG = colors.HexColor('#eafaf1')
COLOR_FAIL_BG = colors.HexColor('#fdedec')
COLOR_IGN_BG  = colors.HexColor('#fef9e7')


# Sequências ANSI (cores no terminal) que o Unity injeta com
# UNITY_OUTPUT_COLOR. Removidas antes do parsing.
_ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')


# ============================================================================
#  Estilos compartilhados
# ============================================================================

def _make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        'title': ParagraphStyle(
            'Title', parent=base['Title'], fontName='Helvetica-Bold',
            fontSize=22, textColor=COLOR_NEUTRAL, spaceAfter=2*mm, alignment=0,
        ),
        'subtitle': ParagraphStyle(
            'Subtitle', parent=base['Normal'], fontName='Helvetica',
            fontSize=10, textColor=COLOR_MUTED, spaceAfter=6*mm,
        ),
        'section': ParagraphStyle(
            'Section', parent=base['Heading2'], fontName='Helvetica-Bold',
            fontSize=14, textColor=COLOR_NEUTRAL,
            spaceBefore=6*mm, spaceAfter=3*mm,
        ),
        'subsection': ParagraphStyle(
            'Subsection', parent=base['Heading3'], fontName='Helvetica-Bold',
            fontSize=11, textColor=COLOR_NEUTRAL,
            spaceBefore=3*mm, spaceAfter=2*mm,
        ),
        'mono': ParagraphStyle(
            'Mono', parent=base['Normal'], fontName='Courier',
            fontSize=8, textColor=COLOR_NEUTRAL, leading=10, wordWrap='CJK',
        ),
        'small_muted': ParagraphStyle(
            'SmallMuted', parent=base['Normal'], fontName='Helvetica',
            fontSize=9, textColor=COLOR_MUTED, spaceAfter=2*mm,
        ),
    }


# ============================================================================
#  Unity — parser
# ============================================================================

@dataclass
class UnityTest:
    file:    str
    line:    int
    name:    str
    status:  str   # PASS / FAIL / IGNORE
    message: str


@dataclass
class UnitySummary:
    tests:      list[UnityTest]
    total:      int
    failures:   int
    ignored:    int
    overall_ok: bool


_UNITY_TEST_LINE = re.compile(
    r'^(?P<file>[^:]+):(?P<line>\d+):(?P<name>[^:]+):'
    r'(?P<status>PASS|FAIL|IGNORE)(?::\s*(?P<msg>.*))?$'
)
_UNITY_SUMMARY_LINE = re.compile(
    r'^(?P<total>\d+)\s+Tests?\s+'
    r'(?P<failures>\d+)\s+Failures?\s+'
    r'(?P<ignored>\d+)\s+Ignored',
    re.IGNORECASE,
)


def parse_unity_output(text: str) -> UnitySummary:
    """
    Parseia stdout do Unity em modo verbose (-v).

    Remove sequências ANSI antes (UNITY_OUTPUT_COLOR injeta cor que
    quebra o regex). Linhas que não casam com nenhum padrão são
    ignoradas (prints do código sob teste, mensagens do tddl, etc.).

    Se a linha de sumário "N Tests M Failures K Ignored" não for
    encontrada (output cortado), os contadores são derivados da
    lista de testes parseados.
    """
    text = _ANSI_ESCAPE.sub('', text)

    tests: list[UnityTest] = []
    total = failures = ignored = 0
    saw_summary = False
    overall_ok = False

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        m = _UNITY_TEST_LINE.match(line)
        if m:
            tests.append(UnityTest(
                file=m.group('file'),
                line=int(m.group('line')),
                name=m.group('name'),
                status=m.group('status'),
                message=(m.group('msg') or '').strip(),
            ))
            continue

        m = _UNITY_SUMMARY_LINE.match(line)
        if m:
            total       = int(m.group('total'))
            failures    = int(m.group('failures'))
            ignored     = int(m.group('ignored'))
            saw_summary = True
            continue

        if line == 'OK':
            overall_ok = True

    if not saw_summary and tests:
        total      = len(tests)
        failures   = sum(1 for t in tests if t.status == 'FAIL')
        ignored    = sum(1 for t in tests if t.status == 'IGNORE')
        overall_ok = (failures == 0)

    return UnitySummary(
        tests=tests, total=total, failures=failures,
        ignored=ignored, overall_ok=overall_ok,
    )


# ============================================================================
#  Lizard — parser
# ============================================================================

@dataclass
class LizardFunction:
    name:   str
    file:   str
    start:  int
    end:    int
    nloc:   int
    ccn:    int
    length: int
    params: int
    tokens: int
    violations: list[str] = field(default_factory=list)  # ['ccn'/'length'/'args']

    @property
    def has_violation(self) -> bool:
        return bool(self.violations)


@dataclass
class LizardFileReport:
    """Resultados do lizard num único arquivo (test_file ou src_file)."""
    label:     str    # "test" / "src"
    file_path: Path
    functions: list[LizardFunction]

    @property
    def total_functions(self) -> int:
        return len(self.functions)

    @property
    def violating_functions(self) -> int:
        return sum(1 for f in self.functions if f.has_violation)

    @property
    def clean(self) -> bool:
        return self.violating_functions == 0


@dataclass
class LizardSummary:
    """Resultados completos do lizard nesta execução."""
    files:     list[LizardFileReport]
    ccn_th:    int
    length_th: int
    args_th:   int

    @property
    def clean(self) -> bool:
        return all(f.clean for f in self.files)

    @property
    def total_functions(self) -> int:
        return sum(f.total_functions for f in self.files)

    @property
    def total_violations(self) -> int:
        return sum(f.violating_functions for f in self.files)


def parse_lizard_csv(
    csv_text: str, ccn_th: int, length_th: int, args_th: int,
) -> list[LizardFunction]:
    """
    Parseia output `lizard --csv`.

    Colunas (zero-indexed):
        0: NLOC, 1: CCN, 2: tokens, 3: parameter count, 4: length,
        5: location ("name@start-end@file"), 6: file, 7: name,
        8: long_name, 9: start_line, 10: end_line

    Cada função recebe a lista de thresholds que violou, calculada
    aqui contra os thresholds passados (não confiamos no -w do lizard
    porque ele só filtra a saída texto).
    """
    functions: list[LizardFunction] = []
    reader = csv.reader(io.StringIO(csv_text))
    for row in reader:
        if len(row) < 11:
            continue
        try:
            nloc   = int(row[0])
            ccn    = int(row[1])
            tokens = int(row[2])
            params = int(row[3])
            length = int(row[4])
            start  = int(row[9])
            end    = int(row[10])
        except ValueError:
            continue   # cabeçalho ou linha não-numérica

        fn = LizardFunction(
            name=row[7], file=row[6],
            start=start, end=end,
            nloc=nloc, ccn=ccn, length=length, params=params, tokens=tokens,
        )
        if ccn    > ccn_th:    fn.violations.append('ccn')
        if length > length_th: fn.violations.append('length')
        if params > args_th:   fn.violations.append('args')
        functions.append(fn)
    return functions


# ============================================================================
#  Helpers visuais compartilhados
# ============================================================================

def _hex_for_para(color) -> str:
    """Converte reportlab Color → '#RRGGBB' (formato do tag <font color>)."""
    return '#' + color.hexval()[2:]


def _three_cards(
    values:   tuple[str, str, str],
    labels:   tuple[str, str, str],
    actives:  tuple[bool, bool, bool],
    bg_top:   tuple,
    bg_label: tuple,
    fg_value: tuple,
    inactive_top: object   = COLOR_BG_ROW,
    inactive_label: object = COLOR_MUTED,
    inactive_value: object = COLOR_MUTED,
) -> Table:
    """3 cards lado a lado — esqueleto reutilizável."""
    GAP = ''
    data = [
        [values[0], GAP, values[1], GAP, values[2]],
        [labels[0], GAP, labels[1], GAP, labels[2]],
    ]
    page_width = A4[0] - 30*mm
    gap_w  = 3*mm
    card_w = (page_width - 2*gap_w) / 3.0
    t = Table(data,
              colWidths=[card_w, gap_w, card_w, gap_w, card_w],
              rowHeights=[18*mm, 8*mm])

    def top(i):    return bg_top[i]   if actives[i] else inactive_top
    def lab(i):    return bg_label[i] if actives[i] else inactive_label
    def val(i):    return fg_value[i] if actives[i] else inactive_value

    style = [
        ('FONTNAME',  (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',  (0, 0), (-1, 0), 32),
        ('ALIGN',     (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN',    (0, 0), (-1, 0), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (0, 0), val(0)),
        ('TEXTCOLOR', (2, 0), (2, 0), val(1)),
        ('TEXTCOLOR', (4, 0), (4, 0), val(2)),
        ('BACKGROUND', (0, 0), (0, 0), top(0)),
        ('BACKGROUND', (2, 0), (2, 0), top(1)),
        ('BACKGROUND', (4, 0), (4, 0), top(2)),

        ('FONTNAME',  (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE',  (0, 1), (-1, 1), 9),
        ('ALIGN',     (0, 1), (-1, 1), 'CENTER'),
        ('VALIGN',    (0, 1), (-1, 1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 1), (0, 1), lab(0)),
        ('BACKGROUND', (2, 1), (2, 1), lab(1)),
        ('BACKGROUND', (4, 1), (4, 1), lab(2)),

        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]
    t.setStyle(TableStyle(style))
    return t


# ============================================================================
#  Seção Unity
# ============================================================================

def _status_color(status: str):
    return {'PASS': COLOR_PASS, 'FAIL': COLOR_FAIL, 'IGNORE': COLOR_IGNORE}.get(
        status, COLOR_NEUTRAL
    )


def _unity_cards(summary: UnitySummary) -> Table:
    passed = summary.total - summary.failures - summary.ignored
    return _three_cards(
        values  = (str(passed), str(summary.failures), str(summary.ignored)),
        labels  = ('PASSED', 'FAILED', 'IGNORED'),
        actives = (True, summary.failures > 0, summary.ignored > 0),
        bg_top   = (COLOR_PASS_BG, COLOR_FAIL_BG, COLOR_IGN_BG),
        bg_label = (COLOR_PASS,    COLOR_FAIL,    COLOR_IGNORE),
        fg_value = (COLOR_PASS,    COLOR_FAIL,    COLOR_IGNORE),
    )


def _unity_tests_table(tests: list[UnityTest], styles: dict) -> Table:
    """Tabela: Status | Test | Line | Message."""
    header = ['Status', 'Test', 'Line', 'Message']
    rows: list[list] = [header]

    name_style = ParagraphStyle(
        'TestName', parent=styles['mono'], fontSize=8, leading=10, wordWrap='CJK',
    )

    for t in tests:
        msg_text = t.message if t.message else '—'
        safe_msg = msg_text.replace('<', '&lt;').replace('>', '&gt;')
        msg_style = (
            styles['mono'] if t.status == 'PASS' else
            ParagraphStyle(
                'msg_inline', parent=styles['mono'],
                textColor=_status_color(t.status), wordWrap='CJK',
            )
        )
        safe_name = t.name.replace('<', '&lt;').replace('>', '&gt;')
        rows.append([
            t.status,
            Paragraph(safe_name, name_style),
            str(t.line),
            Paragraph(safe_msg, msg_style),
        ])

    page_width = A4[0] - 30*mm
    col_widths = [18*mm, page_width * 0.45, 13*mm, None]
    used = sum(w for w in col_widths if w is not None)
    col_widths[-1] = page_width - used

    table = Table(rows, colWidths=col_widths, repeatRows=1)

    cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_HEADER),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 9),
        ('ALIGN',      (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN',      (2, 0), (2, 0),  'RIGHT'),
        ('FONTNAME',   (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 1), (-1, -1), 8.5),
        ('VALIGN',     (0, 1), (-1, -1), 'TOP'),
        ('ALIGN',      (2, 1), (2, -1),  'RIGHT'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 3),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 3),
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, 0), (-1, -1), 0.25, COLOR_MUTED),
    ]
    for i, t in enumerate(tests, start=1):
        cmds.append(('TEXTCOLOR', (0, i), (0, i), _status_color(t.status)))
        cmds.append(('FONTNAME',  (0, i), (0, i), 'Helvetica-Bold'))
        if i % 2 == 0:
            cmds.append(('BACKGROUND', (0, i), (-1, i), COLOR_BG_ROW))
    table.setStyle(TableStyle(cmds))
    return table


def _unity_section(summary: UnitySummary, styles: dict) -> list:
    overall_label = 'OK' if summary.overall_ok else 'FAILED'
    overall_color = COLOR_PASS if summary.overall_ok else COLOR_FAIL

    out: list = [
        Paragraph(
            f'<font color="{_hex_for_para(overall_color)}"><b>{overall_label}</b></font> '
            f'— {summary.total} tests run, '
            f'{summary.failures} failed, '
            f'{summary.ignored} ignored',
            styles['small_muted'],
        ),
        Spacer(1, 2*mm),
        _unity_cards(summary),
        Spacer(1, 5*mm),
        Paragraph('Test results', styles['subsection']),
    ]
    if summary.tests:
        out.append(_unity_tests_table(summary.tests, styles))
    else:
        out.append(Paragraph(
            '<i>No test results were parsed from the Unity output.</i>',
            ParagraphStyle('e', parent=styles['mono'], textColor=COLOR_MUTED),
        ))
    return out


# ============================================================================
#  Seção Lizard
# ============================================================================

def _lizard_cards(summary: LizardSummary) -> Table:
    has_viol = summary.total_violations > 0
    return _three_cards(
        values   = (str(summary.total_functions),
                    str(summary.total_violations),
                    str(len(summary.files))),
        labels   = ('FUNCTIONS', 'VIOLATIONS', 'FILES'),
        actives  = (True, has_viol, True),
        bg_top   = (COLOR_BG_ROW, COLOR_VIOL_BG, COLOR_BG_ROW),
        bg_label = (COLOR_NEUTRAL, COLOR_FAIL,    COLOR_NEUTRAL),
        fg_value = (COLOR_NEUTRAL, COLOR_FAIL,    COLOR_NEUTRAL),
    )


def _lizard_file_table(file_report: LizardFileReport, styles: dict) -> Table:
    """Tabela: Function | NLOC | CCN | Length | Args | Tokens | Location."""
    header = ['Function', 'NLOC', 'CCN', 'Length', 'Args', 'Tokens', 'Location']
    rows: list[list] = [header]

    name_style = ParagraphStyle(
        'FnName', parent=styles['mono'], fontSize=8, leading=10, wordWrap='CJK',
    )
    loc_style = ParagraphStyle(
        'Loc', parent=styles['mono'], fontSize=7.5,
        textColor=COLOR_MUTED, leading=9, wordWrap='CJK',
    )

    for fn in file_report.functions:
        loc = f'{fn.file}:{fn.start}-{fn.end}'
        rows.append([
            Paragraph(fn.name, name_style),
            str(fn.nloc), str(fn.ccn), str(fn.length),
            str(fn.params), str(fn.tokens),
            Paragraph(loc, loc_style),
        ])

    page_width = A4[0] - 30*mm
    fn_w  = page_width * 0.30
    loc_w = page_width * 0.30
    num_w = (page_width - fn_w - loc_w) / 5.0
    col_widths = [fn_w, num_w, num_w, num_w, num_w, num_w, loc_w]

    table = Table(rows, colWidths=col_widths, repeatRows=1)

    cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_HEADER),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 9),
        ('ALIGN',      (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN',      (1, 0), (5, -1), 'RIGHT'),
        ('FONTNAME',   (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 1), (-1, -1), 8.5),
        ('VALIGN',     (0, 1), (-1, -1), 'TOP'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 3),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 3),
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, 0), (-1, -1), 0.25, COLOR_MUTED),
    ]

    for i, fn in enumerate(file_report.functions, start=1):
        if fn.has_violation:
            cmds.append(('BACKGROUND', (0, i), (-1, i), COLOR_VIOL_BG))
            for viol in fn.violations:
                col_idx = {'ccn': 2, 'length': 3, 'args': 4}[viol]
                cmds.append(('TEXTCOLOR', (col_idx, i), (col_idx, i), COLOR_FAIL))
                cmds.append(('FONTNAME',  (col_idx, i), (col_idx, i), 'Helvetica-Bold'))
        elif i % 2 == 0:
            cmds.append(('BACKGROUND', (0, i), (-1, i), COLOR_BG_ROW))

    table.setStyle(TableStyle(cmds))
    return table


def _lizard_section(summary: LizardSummary, styles: dict) -> list:
    overall_label = 'OK' if summary.clean else 'VIOLATIONS'
    overall_color = COLOR_PASS if summary.clean else COLOR_FAIL

    out: list = [
        Paragraph(
            f'<font color="{_hex_for_para(overall_color)}"><b>{overall_label}</b></font> '
            f'— {summary.total_functions} functions, '
            f'{summary.total_violations} violations, '
            f'{len(summary.files)} file(s)',
            styles['small_muted'],
        ),
        Paragraph(
            f'Thresholds: CCN ≤ {summary.ccn_th}, '
            f'length ≤ {summary.length_th}, '
            f'args ≤ {summary.args_th}',
            ParagraphStyle('th', parent=styles['small_muted'],
                           textColor=COLOR_NEUTRAL, fontSize=9),
        ),
        Spacer(1, 2*mm),
        _lizard_cards(summary),
        Spacer(1, 5*mm),
    ]
    for fr in summary.files:
        out.append(Paragraph(
            f'<b>{fr.label}</b> — {fr.file_path.name}',
            styles['subsection']
        ))
        if fr.functions:
            out.append(_lizard_file_table(fr, styles))
        else:
            out.append(Paragraph(
                '<i>No functions analyzed in this file.</i>',
                ParagraphStyle('e', parent=styles['mono'], textColor=COLOR_MUTED),
            ))
        out.append(Spacer(1, 3*mm))
    return out


# ============================================================================
#  Valgrind — parser
# ============================================================================
#
# Valgrind escreve em stderr no formato:
#
#   ==12345== Memcheck, a memory error detector
#   ==12345== Copyright (C) ...
#   ==12345== Command: ./tddl_foo -v
#   ==12345==
#   ==12345== Invalid read of size 4
#   ==12345==    at 0x401234: foo (foo.c:12)
#   ==12345==    by 0x405678: main (test_foo.c:34)
#   ==12345==  Address 0x... is 0 bytes after a block of size 4 alloc'd
#   ==12345==    at 0x...: malloc (...)
#   ==12345==    by 0x...: foo (foo.c:8)
#   ==12345==
#   ==12345== HEAP SUMMARY:
#   ==12345==     in use at exit: 8 bytes in 1 blocks
#   ==12345==   total heap usage: 3 allocs, 2 frees, 1,032 bytes allocated
#   ==12345==
#   ==12345== 8 bytes in 1 blocks are definitely lost in loss record 1 of 1
#   ==12345==    at 0x...: malloc (...)
#   ==12345==    by 0x...: foo (foo.c:8)
#   ==12345==    by 0x...: main (test_foo.c:30)
#   ==12345==
#   ==12345== LEAK SUMMARY:
#   ==12345==    definitely lost: 8 bytes in 1 blocks
#   ==12345==    indirectly lost: 0 bytes in 0 blocks
#   ==12345==      possibly lost: 0 bytes in 0 blocks
#   ==12345==    still reachable: 0 bytes in 0 blocks
#   ==12345==         suppressed: 0 bytes in 0 blocks
#   ==12345==
#   ==12345== ERROR SUMMARY: 2 errors from 2 contexts (suppressed: 0 from 0)
#
# O parser:
#   1. Tira o prefixo "==PID==" de toda linha.
#   2. Quebra em "blocos" separados por linhas em branco.
#   3. Classifica cada bloco: leak/error/heap/leak_summary/error_summary/banner.
#   4. Extrai stack frames das linhas "at" e "by".

# Cores específicas para categorias de leak / erro do Valgrind.
COLOR_LEAK_DEFINITE   = colors.HexColor('#c0392b')   # vermelho — pior
COLOR_LEAK_INDIRECT   = colors.HexColor('#d35400')   # laranja escuro
COLOR_LEAK_POSSIBLE   = colors.HexColor('#b58900')   # amarelo
COLOR_LEAK_REACHABLE  = colors.HexColor('#2980b9')   # azul — informativo
COLOR_LEAK_SUPPRESSED = COLOR_MUTED                  # cinza

# Cabeçalhos típicos de bloco "erro" do valgrind. Não é uma lista exaustiva
# (o memcheck tem dezenas), mas cobre os mais comuns; qualquer linha que
# não case com um padrão conhecido vira "Other error" para evitar engolir
# diagnósticos silenciosamente.
_VALGRIND_ERROR_HEADS = (
    'Invalid read',
    'Invalid write',
    'Invalid free',
    'Mismatched free',
    'Use of uninitialised',
    'Conditional jump or move depends on uninitialised',
    'Syscall param',
    'Source and destination overlap',
    'Argument',
)


@dataclass
class ValgrindFrame:
    """Uma linha de stack ('at 0x...: func (file:line)' ou 'by ...')."""
    addr: str    # '0x401234' ou '' se não houver
    func: str    # nome da função ou '???'
    where: str   # 'file.c:12' / 'in /lib/libc.so' / ''


@dataclass
class ValgrindError:
    kind:     str                  # 'Invalid read of size 4', 'definitely lost: 8 bytes ...'
    category: str                  # 'error' | 'leak'
    severity: str                  # 'definite'|'indirect'|'possible'|'reachable'|'error'
    frames:   list[ValgrindFrame]  # stack trace principal


@dataclass
class ValgrindLeakCounts:
    """Bytes/blocks de uma categoria do LEAK SUMMARY."""
    bytes_:  int
    blocks:  int

    @property
    def empty(self) -> bool:
        return self.bytes_ == 0 and self.blocks == 0


@dataclass
class ValgrindHeapUsage:
    """
    Resumo do bloco HEAP SUMMARY do valgrind, ex:

      HEAP SUMMARY:
          in use at exit: 8 bytes in 1 blocks
        total heap usage: 3 allocs, 2 frees, 1,032 bytes allocated

    Quando o programa libera tudo direitinho, o valgrind escreve apenas
    "All heap blocks were freed -- no leaks are possible" e omite essas
    duas linhas — nesse caso os campos ficam zerados e `present=False`.
    """
    allocs:          int
    frees:           int
    bytes_allocated: int
    in_use_bytes:    int
    in_use_blocks:   int
    present:         bool   # False se nada do HEAP SUMMARY foi capturado


@dataclass
class ValgrindSummary:
    errors:           list[ValgrindError]
    error_count:      int       # total reportado em ERROR SUMMARY
    contexts:         int       # contextos (do ERROR SUMMARY)
    suppressed_count: int
    definitely_lost:  ValgrindLeakCounts
    indirectly_lost:  ValgrindLeakCounts
    possibly_lost:    ValgrindLeakCounts
    still_reachable:  ValgrindLeakCounts
    suppressed_leak:  ValgrindLeakCounts
    heap:             ValgrindHeapUsage
    raw:              str       # diagnóstico bruto, usado se nada parseou

    @property
    def clean(self) -> bool:
        # Reachable e suppressed não bloqueiam (default do valgrind também
        # não falha por reachable). Tudo o resto, sim.
        return (
            self.error_count == 0
            and self.definitely_lost.empty
            and self.indirectly_lost.empty
            and self.possibly_lost.empty
        )

    @property
    def total_lost_bytes(self) -> int:
        return (self.definitely_lost.bytes_
                + self.indirectly_lost.bytes_
                + self.possibly_lost.bytes_)


# Linhas do tipo:
#   ==12345== Invalid read of size 4
# ou para leaks:
#   ==12345== 8 bytes in 1 blocks are definitely lost in loss record 1 of 1
_VG_PID_PREFIX = re.compile(r'^==\d+==\s?')

# "    at 0x401234: foo (foo.c:12)"  /  "    by 0x401234: foo (in /lib/libc.so.6)"
_VG_FRAME = re.compile(
    r'^(?:at|by)\s+'
    r'(?P<addr>0x[0-9A-Fa-f]+):\s+'
    r'(?P<func>.+?)\s+'
    r'\((?P<where>[^)]*)\)\s*$'
)

# "    definitely lost: 1,234 bytes in 5 blocks"
_VG_LEAK_LINE = re.compile(
    r'^\s*(?P<kind>definitely lost|indirectly lost|possibly lost|'
    r'still reachable|suppressed):\s+'
    r'(?P<bytes>[\d,]+)\s+bytes\s+in\s+'
    r'(?P<blocks>[\d,]+)\s+blocks\s*$',
    re.IGNORECASE,
)

# "ERROR SUMMARY: 2 errors from 2 contexts (suppressed: 0 from 0)"
_VG_ERROR_SUMMARY = re.compile(
    r'^ERROR SUMMARY:\s+(?P<errors>[\d,]+)\s+errors?\s+from\s+'
    r'(?P<contexts>[\d,]+)\s+contexts?'
    r'(?:\s+\(suppressed:\s+(?P<sup>[\d,]+)\s+from\s+[\d,]+\))?',
    re.IGNORECASE,
)

# "8 bytes in 1 blocks are definitely lost in loss record 1 of 1"
_VG_LEAK_HEADER = re.compile(
    r'^(?P<bytes>[\d,]+)\s+bytes\s+in\s+(?P<blocks>[\d,]+)\s+blocks?\s+are\s+'
    r'(?P<kind>definitely lost|indirectly lost|possibly lost|still reachable)\s+',
    re.IGNORECASE,
)

# "  total heap usage: 147 allocs, 147 frees, 9,664 bytes allocated"
_VG_HEAP_TOTAL = re.compile(
    r'^\s*total\s+heap\s+usage:\s+'
    r'(?P<allocs>[\d,]+)\s+allocs?,\s+'
    r'(?P<frees>[\d,]+)\s+frees?,\s+'
    r'(?P<bytes>[\d,]+)\s+bytes\s+allocated\s*$',
    re.IGNORECASE,
)

# "     in use at exit: 8 bytes in 1 blocks"
_VG_HEAP_INUSE = re.compile(
    r'^\s*in\s+use\s+at\s+exit:\s+'
    r'(?P<bytes>[\d,]+)\s+bytes\s+in\s+'
    r'(?P<blocks>[\d,]+)\s+blocks?\s*$',
    re.IGNORECASE,
)


def _atoi(s: str) -> int:
    """Valgrind imprime números com vírgula como milhar — '1,234' → 1234."""
    try:
        return int(s.replace(',', ''))
    except (ValueError, AttributeError):
        return 0


def _strip_vg_prefix(text: str) -> list[str]:
    """Remove '==PID== ' de cada linha; descarta linhas sem o prefixo
    (ruído de outras ferramentas misturado no stderr)."""
    out: list[str] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            out.append('')
            continue
        m = _VG_PID_PREFIX.match(line)
        if m:
            out.append(line[m.end():])
        # linhas sem prefixo são descartadas — não fazem parte do output
        # estruturado do valgrind
    return out


def _parse_frame(line: str) -> ValgrindFrame | None:
    line = line.strip()
    m = _VG_FRAME.match(line)
    if not m:
        return None
    return ValgrindFrame(
        addr=m.group('addr'),
        func=m.group('func').strip(),
        where=m.group('where').strip(),
    )


def _classify_error_header(header: str) -> tuple[str, str] | None:
    """
    Retorna (severity, kind) para a primeira linha de um bloco de erro,
    ou None se não parece um erro reconhecível.
    """
    # Leak header tem o formato "N bytes in M blocks are <kind> lost..."
    m = _VG_LEAK_HEADER.match(header)
    if m:
        kind_word = m.group('kind').lower()
        severity = {
            'definitely lost': 'definite',
            'indirectly lost': 'indirect',
            'possibly lost':   'possible',
            'still reachable': 'reachable',
        }[kind_word]
        return (severity, header)

    for prefix in _VALGRIND_ERROR_HEADS:
        if header.startswith(prefix):
            return ('error', header)

    return None


def parse_valgrind_output(text: str) -> ValgrindSummary:
    """
    Parseia stderr do valgrind. Tolerante a partes faltantes: se o LEAK
    SUMMARY não aparecer (sem --leak-check=full numa execução antiga,
    binário abortou cedo, etc.), os counts ficam zerados; se nenhum
    bloco de erro parsear, devolve uma summary com `errors=[]` e o raw
    populado pra debugar.
    """
    raw_text = text  # preserva pra raw view
    lines = _strip_vg_prefix(text)

    # Defaults
    definitely = ValgrindLeakCounts(0, 0)
    indirectly = ValgrindLeakCounts(0, 0)
    possibly   = ValgrindLeakCounts(0, 0)
    reachable  = ValgrindLeakCounts(0, 0)
    suppressed = ValgrindLeakCounts(0, 0)
    heap       = ValgrindHeapUsage(0, 0, 0, 0, 0, present=False)
    error_count = 0
    contexts = 0
    suppressed_count = 0
    errors: list[ValgrindError] = []

    # 1) Quebra em blocos por linha em branco (o valgrind separa cada
    #    erro/seção com '==PID==' sozinho, que após strip vira '').
    block: list[str] = []
    blocks: list[list[str]] = []
    for line in lines:
        if line == '':
            if block:
                blocks.append(block)
                block = []
        else:
            block.append(line)
    if block:
        blocks.append(block)

    # 2) Para cada bloco, decide o que é.
    for blk in blocks:
        head = blk[0].strip()

        # ERROR SUMMARY pode estar sozinho ou como última linha
        for line in blk:
            m_es = _VG_ERROR_SUMMARY.match(line.strip())
            if m_es:
                error_count      = _atoi(m_es.group('errors'))
                contexts         = _atoi(m_es.group('contexts'))
                suppressed_count = _atoi(m_es.group('sup') or '0')

        # HEAP SUMMARY — bloco com "in use at exit" e "total heap usage".
        # Detectado pela presença do cabeçalho "HEAP SUMMARY:" no bloco;
        # as duas linhas seguintes batem nos regex específicos.
        if any('HEAP SUMMARY' in l for l in blk):
            heap_allocs = heap_frees = heap_bytes = 0
            heap_in_b   = heap_in_blk = 0
            heap_got_any = False
            for l in blk:
                m_t = _VG_HEAP_TOTAL.match(l)
                if m_t:
                    heap_allocs = _atoi(m_t.group('allocs'))
                    heap_frees  = _atoi(m_t.group('frees'))
                    heap_bytes  = _atoi(m_t.group('bytes'))
                    heap_got_any = True
                    continue
                m_i = _VG_HEAP_INUSE.match(l)
                if m_i:
                    heap_in_b   = _atoi(m_i.group('bytes'))
                    heap_in_blk = _atoi(m_i.group('blocks'))
                    heap_got_any = True
            if heap_got_any:
                heap = ValgrindHeapUsage(
                    allocs=heap_allocs, frees=heap_frees,
                    bytes_allocated=heap_bytes,
                    in_use_bytes=heap_in_b, in_use_blocks=heap_in_blk,
                    present=True,
                )
            continue   # bloco consumido como HEAP SUMMARY

        # LEAK SUMMARY — bloco onde tem várias linhas "<kind>: N bytes in M blocks"
        leak_lines = [l for l in blk if _VG_LEAK_LINE.match(l)]
        if leak_lines and any('LEAK SUMMARY' in l for l in blk):
            for l in leak_lines:
                m = _VG_LEAK_LINE.match(l)
                assert m  # já filtrado
                kind = m.group('kind').lower()
                counts = ValgrindLeakCounts(
                    bytes_=_atoi(m.group('bytes')),
                    blocks=_atoi(m.group('blocks')),
                )
                if   kind == 'definitely lost': definitely = counts
                elif kind == 'indirectly lost': indirectly = counts
                elif kind == 'possibly lost':   possibly   = counts
                elif kind == 'still reachable': reachable  = counts
                elif kind == 'suppressed':      suppressed = counts
            continue   # bloco consumido como LEAK SUMMARY

        # Bloco de erro propriamente dito (Invalid read, leak record, etc.)
        cls = _classify_error_header(head)
        if cls is None:
            continue
        severity, kind = cls
        frames: list[ValgrindFrame] = []
        for l in blk[1:]:
            f = _parse_frame(l)
            if f is not None:
                frames.append(f)
            # paramos no primeiro "Address ... is ..." pra não inflar com
            # frames secundárias do bloco alloc'd — elas trazem ruído sem
            # ajudar muito no relatório de uma página. Se quiser cobertura
            # completa, dá pra remover esse break.
            elif l.strip().startswith('Address '):
                break
        errors.append(ValgrindError(
            kind=kind,
            category='leak' if severity in ('definite','indirect','possible','reachable')
                              else 'error',
            severity=severity,
            frames=frames,
        ))

    return ValgrindSummary(
        errors=errors,
        error_count=error_count,
        contexts=contexts,
        suppressed_count=suppressed_count,
        definitely_lost=definitely,
        indirectly_lost=indirectly,
        possibly_lost=possibly,
        still_reachable=reachable,
        suppressed_leak=suppressed,
        heap=heap,
        raw=raw_text,
    )


# ============================================================================
#  Valgrind — seção do PDF
# ============================================================================

def _vg_severity_color(severity: str):
    return {
        'definite':  COLOR_LEAK_DEFINITE,
        'indirect':  COLOR_LEAK_INDIRECT,
        'possible':  COLOR_LEAK_POSSIBLE,
        'reachable': COLOR_LEAK_REACHABLE,
        'error':     COLOR_FAIL,
    }.get(severity, COLOR_NEUTRAL)


def _vg_severity_label(severity: str) -> str:
    return {
        'definite':  'DEFINITE LEAK',
        'indirect':  'INDIRECT LEAK',
        'possible':  'POSSIBLE LEAK',
        'reachable': 'REACHABLE',
        'error':     'ERROR',
    }.get(severity, severity.upper())


def _valgrind_cards(summary: ValgrindSummary) -> Table:
    """
    3 cards: Errors | Definitely lost (bytes) | Indirect+Possible (bytes).

    Reachable e suppressed ficam pra tabela de leak summary — não cabem
    nos cards sem poluir.
    """
    errs    = summary.error_count
    def_b   = summary.definitely_lost.bytes_
    other_b = summary.indirectly_lost.bytes_ + summary.possibly_lost.bytes_

    return _three_cards(
        values   = (str(errs), f'{def_b:,}', f'{other_b:,}'),
        labels   = ('ERRORS', 'DEFINITELY LOST', 'INDIRECT+POSSIBLE'),
        actives  = (errs > 0, def_b > 0, other_b > 0),
        bg_top   = (COLOR_FAIL_BG, COLOR_FAIL_BG,        COLOR_IGN_BG),
        bg_label = (COLOR_FAIL,    COLOR_LEAK_DEFINITE,  COLOR_LEAK_POSSIBLE),
        fg_value = (COLOR_FAIL,    COLOR_LEAK_DEFINITE,  COLOR_LEAK_POSSIBLE),
    )


def _valgrind_heap_table(summary: ValgrindSummary, styles: dict) -> Table:
    """
    Tabela compacta com o HEAP SUMMARY do valgrind:
        Allocations | Frees | Bytes allocated | In use at exit
    Renderizada como 4 colunas (label em cima, valor embaixo), igual em
    espírito aos 3-cards mas em formato mais discreto pra info auxiliar.
    """
    h = summary.heap
    leaked = h.allocs - h.frees           # nº de blocos não liberados

    in_use_str = f'{h.in_use_bytes:,} bytes ({h.in_use_blocks:,} blocks)'
    if h.in_use_bytes == 0 and h.in_use_blocks == 0:
        in_use_str = '0 bytes (0 blocks)'

    values = [
        f'{h.allocs:,}',
        f'{h.frees:,}',
        f'{h.bytes_allocated:,}',
        in_use_str,
    ]
    labels = ['ALLOCATIONS', 'FREES', 'BYTES ALLOCATED', 'IN USE AT EXIT']

    rows = [values, labels]

    page_width = A4[0] - 30*mm
    col_w = page_width / 4.0
    t = Table(rows, colWidths=[col_w]*4, rowHeights=[11*mm, 6*mm])

    # Cor da última coluna ("in use at exit"): vermelha se sobrou bloco,
    # neutra se zerou. Sinaliza visualmente vazamento bruto.
    leaked_color  = COLOR_FAIL if leaked > 0 else COLOR_PASS
    leaked_bg     = COLOR_VIOL_BG if leaked > 0 else COLOR_PASS_BG

    style = [
        # Linha dos valores
        ('FONTNAME',  (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',  (0, 0), (-1, 0), 14),
        ('ALIGN',     (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN',    (0, 0), (-1, 0), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (2, 0), COLOR_NEUTRAL),
        ('TEXTCOLOR', (3, 0), (3, 0), leaked_color),
        ('BACKGROUND', (0, 0), (2, 0), COLOR_BG_ROW),
        ('BACKGROUND', (3, 0), (3, 0), leaked_bg),

        # Linha dos labels
        ('FONTNAME',  (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE',  (0, 1), (-1, 1), 8),
        ('ALIGN',     (0, 1), (-1, 1), 'CENTER'),
        ('VALIGN',    (0, 1), (-1, 1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 1), (2, 1), COLOR_NEUTRAL),
        ('BACKGROUND', (3, 1), (3, 1), leaked_color),

        ('LEFTPADDING',   (0, 0), (-1, -1), 1),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 1),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]
    t.setStyle(TableStyle(style))
    return t


def _valgrind_leak_table(summary: ValgrindSummary, styles: dict) -> Table:
    """Tabela com as 5 categorias do LEAK SUMMARY."""
    rows = [['Category', 'Bytes', 'Blocks']]
    cats = [
        ('Definitely lost', summary.definitely_lost,  'definite'),
        ('Indirectly lost', summary.indirectly_lost,  'indirect'),
        ('Possibly lost',   summary.possibly_lost,    'possible'),
        ('Still reachable', summary.still_reachable,  'reachable'),
        ('Suppressed',      summary.suppressed_leak,  None),
    ]
    for label, counts, _sev in cats:
        rows.append([label, f'{counts.bytes_:,}', f'{counts.blocks:,}'])

    page_width = A4[0] - 30*mm
    col_widths = [page_width * 0.55, page_width * 0.225, page_width * 0.225]
    t = Table(rows, colWidths=col_widths, repeatRows=1)

    cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_HEADER),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 9),
        ('ALIGN',      (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN',      (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME',   (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE',   (0, 1), (-1, -1), 9),
        ('VALIGN',     (0, 1), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 4),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, 0), (-1, -1), 0.25, COLOR_MUTED),
    ]
    for i, (_lbl, counts, sev) in enumerate(cats, start=1):
        nonzero = not counts.empty
        if nonzero and sev is not None:
            cmds.append(('TEXTCOLOR', (0, i), (0, i), _vg_severity_color(sev)))
            cmds.append(('FONTNAME',  (0, i), (0, i), 'Helvetica-Bold'))
            cmds.append(('BACKGROUND', (0, i), (-1, i), COLOR_VIOL_BG))
        elif i % 2 == 0:
            cmds.append(('BACKGROUND', (0, i), (-1, i), COLOR_BG_ROW))
    t.setStyle(TableStyle(cmds))
    return t


def _valgrind_error_block(err: ValgrindError, idx: int, styles: dict) -> Table:
    """
    Renderiza um único erro como uma mini-tabela:
        [ SEVERITY ]  kind...
                      at  0x...: func (file:line)
                      by  0x...: ...
    """
    sev_color = _vg_severity_color(err.severity)
    sev_label = _vg_severity_label(err.severity)

    kind_para = Paragraph(
        f'<font color="{_hex_for_para(sev_color)}"><b>#{idx} {sev_label}</b></font> '
        f'— {err.kind.replace("<", "&lt;").replace(">", "&gt;")}',
        ParagraphStyle('vg_kind', parent=styles['mono'],
                       fontSize=8.5, leading=11, wordWrap='CJK'),
    )

    frame_style = ParagraphStyle(
        'vg_frame', parent=styles['mono'],
        fontSize=8, leading=10, wordWrap='CJK',
        textColor=COLOR_NEUTRAL,
    )

    rows = [[kind_para]]
    if err.frames:
        for i, f in enumerate(err.frames):
            tag = 'at' if i == 0 else 'by'
            line = (
                f'<font color="{_hex_for_para(COLOR_MUTED)}">{tag}</font> '
                f'{f.addr}: <b>{f.func.replace("<","&lt;").replace(">","&gt;")}</b> '
                f'<font color="{_hex_for_para(COLOR_MUTED)}">'
                f'({f.where.replace("<","&lt;").replace(">","&gt;") or "??"})</font>'
            )
            rows.append([Paragraph(line, frame_style)])
    else:
        rows.append([Paragraph(
            '<i>No stack frames parsed.</i>',
            ParagraphStyle('vg_nf', parent=styles['mono'], textColor=COLOR_MUTED),
        )])

    page_width = A4[0] - 30*mm
    t = Table(rows, colWidths=[page_width])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), COLOR_VIOL_BG),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW',     (0, 0), (-1, -1), 0.25, COLOR_MUTED),
        ('LINEBEFORE',    (0, 0), (0, -1),  2,    sev_color),
    ]))
    return t


def _valgrind_section(summary: ValgrindSummary, styles: dict) -> list:
    overall_label = 'OK' if summary.clean else 'ERRORS DETECTED'
    overall_color = COLOR_PASS if summary.clean else COLOR_FAIL

    header_line = (
        f'<font color="{_hex_for_para(overall_color)}"><b>{overall_label}</b></font> '
        f'— {summary.error_count} error(s) from {summary.contexts} context(s), '
        f'{summary.total_lost_bytes:,} byte(s) lost'
    )
    if summary.suppressed_count:
        header_line += f', {summary.suppressed_count} suppressed'

    out: list = [
        Paragraph(header_line, styles['small_muted']),
        Spacer(1, 2*mm),
        _valgrind_cards(summary),
        Spacer(1, 5*mm),
    ]

    # Heap usage — só renderiza se o valgrind chegou a emitir o
    # HEAP SUMMARY (programas que segfaultam antes do exit não emitem).
    if summary.heap.present:
        out.append(Paragraph('Heap usage', styles['subsection']))
        out.append(_valgrind_heap_table(summary, styles))
        out.append(Spacer(1, 4*mm))

    out.append(Paragraph('Leak summary', styles['subsection']))
    out.append(_valgrind_leak_table(summary, styles))
    out.append(Spacer(1, 4*mm))

    # Lista de erros (cada um numa "caixinha" colorida pela severidade).
    if summary.errors:
        out.append(Paragraph(
            f'Errors & leaks ({len(summary.errors)})', styles['subsection']
        ))
        for i, err in enumerate(summary.errors, start=1):
            out.append(_valgrind_error_block(err, i, styles))
            out.append(Spacer(1, 1.5*mm))
    elif summary.error_count == 0 and summary.clean:
        out.append(Paragraph(
            '<i>No memory errors or leaks detected.</i>',
            ParagraphStyle('e', parent=styles['mono'], textColor=COLOR_MUTED),
        ))
    else:
        # Valgrind reportou contadores mas não conseguimos parsear os
        # blocos individuais — mostra o raw bruto pra não perder info.
        out.append(Paragraph(
            '<i>Could not parse individual error blocks. '
            'Showing raw valgrind output:</i>',
            ParagraphStyle('e', parent=styles['mono'], textColor=COLOR_MUTED),
        ))
        # Limita o raw pra não estourar o PDF se vier gigante.
        raw_clip = summary.raw[:8000]
        if len(summary.raw) > 8000:
            raw_clip += '\n... (truncated)'
        safe_raw = raw_clip.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        out.append(Paragraph(
            safe_raw.replace('\n', '<br/>'),
            ParagraphStyle('vg_raw', parent=styles['mono'],
                           fontSize=7.5, leading=9, wordWrap='CJK'),
        ))

    return out


# ============================================================================
#  Capa (metadata global)
# ============================================================================

def _cover_metadata(
    test_file: Path, src_file: Path | None, mode: str, run_dt: datetime,
) -> Table:
    rows = [['Arquivo:', str(test_file)]]
    if src_file is not None:
        rows.append(['Src:', str(src_file)])
    rows.append(['Modo:',      mode])
    rows.append(['Executado:', run_dt.strftime('%Y-%m-%d %H:%M:%S')])

    t = Table(rows, colWidths=[28*mm, None])
    t.setStyle(TableStyle([
        ('FONTNAME',  (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME',  (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE',  (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), COLOR_MUTED),
        ('TEXTCOLOR', (1, 0), (1, -1), COLOR_NEUTRAL),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5*mm),
        ('TOPPADDING',    (0, 0), (-1, -1), 0.5*mm),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
    ]))
    return t


def _global_status(
    unity:    UnitySummary    | None,
    lizard:   LizardSummary   | None,
    valgrind: ValgrindSummary | None = None,
) -> tuple[bool, list[str]]:
    """Decide o status global. Coerente com o exit code do tddl."""
    failures: list[str] = []
    if unity is not None and not unity.overall_ok:
        failures.append('tests')
    if lizard is not None and not lizard.clean:
        failures.append('lizard')
    if valgrind is not None and not valgrind.clean:
        failures.append('valgrind')
    return (not failures), failures


# ============================================================================
#  Entry point único
# ============================================================================

def generate_combined_pdf(
    output_path: Path,
    test_file:   Path,
    src_file:    Path | None,
    mode:        str,
    run_dt:      datetime,
    unity:       UnitySummary    | None = None,
    lizard:      LizardSummary   | None = None,
    valgrind:    ValgrindSummary | None = None,
) -> None:
    """
    Gera o PDF combinado. Cada ferramenta vira uma seção; se o summary
    correspondente for None, a seção é omitida (sem páginas vazias).

    Este é o único ponto de entrada usado pelo __main__.py.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm,  bottomMargin=15*mm,
        title=f'tddl report — {test_file.name}',
        author='tddl',
    )

    styles = _make_styles()
    ok, reasons = _global_status(unity, lizard, valgrind)
    status_label = 'OK' if ok else 'FAILED'
    status_color = COLOR_PASS if ok else COLOR_FAIL

    elements: list = [
        Paragraph('tddl Report', styles['title']),
        Paragraph(
            f'<font color="{_hex_for_para(status_color)}"><b>{status_label}</b></font>'
            + (f' — failures in: {", ".join(reasons)}' if reasons else ''),
            styles['subtitle'],
        ),
        _cover_metadata(test_file, src_file, mode, run_dt),
        Spacer(1, 6*mm),
    ]

    # Helper: separa seções com uma quebra condicional. CondPageBreak só
    # quebra se restar pouco espaço — evita páginas em branco quando a
    # seção anterior já tinha empurrado o conteúdo pra uma nova página.
    _has_section = False
    def _maybe_break():
        nonlocal _has_section
        if _has_section:
            # ~120mm é folga generosa pra começar uma nova seção com
            # cards + tabela visíveis ainda na mesma página
            elements.append(CondPageBreak(120*mm))
        _has_section = True

    if unity is not None:
        _maybe_break()
        elements.append(Paragraph('Unity tests', styles['section']))
        elements.extend(_unity_section(unity, styles))

    if valgrind is not None:
        _maybe_break()
        elements.append(Paragraph('Valgrind memory check', styles['section']))
        elements.extend(_valgrind_section(valgrind, styles))

    if lizard is not None:
        _maybe_break()
        elements.append(Paragraph('Lizard complexity', styles['section']))
        elements.extend(_lizard_section(lizard, styles))

    doc.build(elements)