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
    unity: UnitySummary | None,
    lizard: LizardSummary | None,
) -> tuple[bool, list[str]]:
    """Decide o status global. Coerente com o exit code do tddl."""
    failures: list[str] = []
    if unity is not None and not unity.overall_ok:
        failures.append('tests')
    if lizard is not None and not lizard.clean:
        failures.append('lizard')
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
    unity:       UnitySummary  | None = None,
    lizard:      LizardSummary | None = None,
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
    ok, reasons = _global_status(unity, lizard)
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

    if unity is not None:
        elements.append(Paragraph('Unity tests', styles['section']))
        elements.extend(_unity_section(unity, styles))

    if lizard is not None:
        # Quebra de página antes de lizard se também tivermos unity,
        # pra não amontoar tudo numa página só.
        if unity is not None:
            elements.append(PageBreak())
        elements.append(Paragraph('Lizard complexity', styles['section']))
        elements.extend(_lizard_section(lizard, styles))

    doc.build(elements)