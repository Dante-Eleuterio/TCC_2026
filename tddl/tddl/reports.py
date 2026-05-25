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
Geração de relatórios em PDF a partir das saídas das ferramentas.

Este módulo contém:
  - Parsers que convertem texto bruto em estruturas tipadas.
  - Geradores que pegam essas estruturas e produzem PDFs.

A ideia é manter o parsing separado do rendering, para que possamos
testar cada parte isoladamente e adicionar outros formatos (HTML, JSON)
no futuro sem mexer no parsing.

Atualmente implementado:
  - Unity (testes)

Próximos:
  - gcovr (cobertura)
  - valgrind (memória)
  - lizard (complexidade)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)


# ============================================================================
#  Paleta de cores compartilhada entre relatórios
# ============================================================================

COLOR_PASS    = colors.HexColor('#1b7f3a')   # verde escuro
COLOR_FAIL    = colors.HexColor('#c0392b')   # vermelho escuro
COLOR_IGNORE  = colors.HexColor('#b58900')   # âmbar
COLOR_NEUTRAL = colors.HexColor('#2c3e50')   # cinza azulado
COLOR_MUTED   = colors.HexColor('#7f8c8d')   # cinza claro
COLOR_BG_ROW  = colors.HexColor('#f4f6f7')   # cinza muito claro (zebrado)
COLOR_HEADER  = colors.HexColor('#34495e')   # cabeçalho de tabela


# ============================================================================
#  Unity — parser
# ============================================================================

@dataclass
class UnityTest:
    file:    str   # caminho do arquivo de teste
    line:    int   # linha onde o teste está declarado
    name:    str   # nome da função (test_xxx)
    status:  str   # PASS / FAIL / IGNORE
    message: str   # mensagem (geralmente em FAIL)


@dataclass
class UnitySummary:
    tests:      list[UnityTest]
    total:      int
    failures:   int
    ignored:    int
    overall_ok: bool


# Regex: file:line:test_name:STATUS[: msg]
# (No Linux/macOS paths não têm ':' no meio.)
_UNITY_TEST_LINE = re.compile(
    r'^(?P<file>[^:]+):(?P<line>\d+):(?P<name>[^:]+):'
    r'(?P<status>PASS|FAIL|IGNORE)(?::\s*(?P<msg>.*))?$'
)

# Sumário Unity: "N Tests M Failures K Ignored"
_UNITY_SUMMARY_LINE = re.compile(
    r'^(?P<total>\d+)\s+Tests?\s+'
    r'(?P<failures>\d+)\s+Failures?\s+'
    r'(?P<ignored>\d+)\s+Ignored',
    re.IGNORECASE,
)

# Códigos ANSI de cor/formatação. Quando UNITY_OUTPUT_COLOR está
# definido no build, o Unity envolve cada PASS/FAIL/IGNORE/OK em
# escape sequences como '\x1b[32m...\x1b[0m'. Como capturamos stdout
# via subprocess para gerar PDF, essas sequências chegam literais e
# atrapalham o regex de linhas. Strippamos antes de parsear.
_ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[A-Za-z]')


def parse_unity_output(text: str) -> UnitySummary:
    """
    Parsear o stdout do Unity em modo verbose (-v).

    Linhas que não casam com nenhum padrão são ignoradas (mensagens
    do tddl, prints do código sob teste, separadores '---').

    Códigos ANSI (gerados quando UNITY_OUTPUT_COLOR está habilitado)
    são removidos antes do match, de modo que cores no terminal não
    quebram o parser.

    Se a linha de sumário não for encontrada (output cortado), os
    contadores são derivados da lista de testes.
    """
    # Primeiro removemos cores ANSI globalmente.
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
#  Unity — gerador de PDF
# ============================================================================

def _status_color(status: str):
    return {'PASS': COLOR_PASS, 'FAIL': COLOR_FAIL, 'IGNORE': COLOR_IGNORE}.get(
        status, COLOR_NEUTRAL
    )


def _make_unity_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        'title': ParagraphStyle(
            'TddlTitle', parent=base['Title'],
            fontName='Helvetica-Bold', fontSize=18,
            textColor=COLOR_NEUTRAL, spaceAfter=2*mm, alignment=0,
        ),
        'subtitle': ParagraphStyle(
            'TddlSubtitle', parent=base['Normal'],
            fontName='Helvetica', fontSize=10,
            textColor=COLOR_MUTED, spaceAfter=6*mm,
        ),
        'section': ParagraphStyle(
            'TddlSection', parent=base['Heading2'],
            fontName='Helvetica-Bold', fontSize=12,
            textColor=COLOR_NEUTRAL, spaceBefore=4*mm, spaceAfter=3*mm,
        ),
        'mono': ParagraphStyle(
            'TddlMono', parent=base['Normal'],
            fontName='Courier', fontSize=8.5, textColor=COLOR_NEUTRAL,
        ),
        'msg': ParagraphStyle(
            'TddlMsg', parent=base['Normal'],
            fontName='Courier', fontSize=8,
            textColor=COLOR_FAIL, leftIndent=2*mm,
        ),
    }


def _unity_metadata_table(test_file: Path, mode: str, run_dt: datetime) -> Table:
    rows = [
        ['Arquivo:',   str(test_file)],
        ['Modo:',      mode],
        ['Executado:', run_dt.strftime('%Y-%m-%d %H:%M:%S')],
    ]
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


def _unity_summary_cards(summary: UnitySummary) -> Table:
    """3 cards PASS/FAIL/IGNORE com número grande + label."""
    passed = summary.total - summary.failures - summary.ignored
    GAP = ''
    data = [
        [str(passed), GAP, str(summary.failures), GAP, str(summary.ignored)],
        ['PASSED',    GAP, 'FAILED',               GAP, 'IGNORED'],
    ]
    page_width = A4[0] - 30*mm
    gap_w  = 3*mm
    card_w = (page_width - 2*gap_w) / 3.0
    t = Table(
        data,
        colWidths=[card_w, gap_w, card_w, gap_w, card_w],
        rowHeights=[18*mm, 8*mm],
    )

    fail_active   = summary.failures > 0
    ignore_active = summary.ignored  > 0

    style = [
        # números grandes (linha 0)
        ('FONTNAME',  (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',  (0, 0), (-1, 0), 32),
        ('ALIGN',     (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN',    (0, 0), (-1, 0), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (0, 0), COLOR_PASS),
        ('TEXTCOLOR', (2, 0), (2, 0), COLOR_FAIL   if fail_active   else COLOR_MUTED),
        ('TEXTCOLOR', (4, 0), (4, 0), COLOR_IGNORE if ignore_active else COLOR_MUTED),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#eafaf1')),
        ('BACKGROUND', (2, 0), (2, 0),
            colors.HexColor('#fdedec') if fail_active   else COLOR_BG_ROW),
        ('BACKGROUND', (4, 0), (4, 0),
            colors.HexColor('#fef9e7') if ignore_active else COLOR_BG_ROW),
        # labels (linha 1)
        ('FONTNAME',  (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE',  (0, 1), (-1, 1), 9),
        ('ALIGN',     (0, 1), (-1, 1), 'CENTER'),
        ('VALIGN',    (0, 1), (-1, 1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 1), (0, 1), COLOR_PASS),
        ('BACKGROUND', (2, 1), (2, 1), COLOR_FAIL   if fail_active   else COLOR_MUTED),
        ('BACKGROUND', (4, 1), (4, 1), COLOR_IGNORE if ignore_active else COLOR_MUTED),
        # padding zerado
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]
    t.setStyle(TableStyle(style))
    return t


def _unity_tests_table(tests: list[UnityTest], styles: dict) -> Table:
    """Tabela detalhada: Status | Test | Line | Message."""
    header = ['Status', 'Test', 'Line', 'Message']
    rows: list[list] = [header]

    # Estilo dedicado pro nome do teste: monospace, mesma cor neutra,
    # e — crucial — usado dentro de um Paragraph para quebrar linhas
    # longas em vez de transbordar pra coluna seguinte.
    name_style = ParagraphStyle(
        'TddlTestName', parent=styles['mono'],
        fontName='Courier', fontSize=8,
        textColor=COLOR_NEUTRAL,
        leading=10,                # espaço entre linhas quebradas
        wordWrap='CJK',            # quebra mesmo em palavras sem espaço
                                   # (necessário para nomes_assim_grandes)
    )

    for t in tests:
        msg_text = t.message if t.message else '—'
        safe_msg = msg_text.replace('<', '&lt;').replace('>', '&gt;')
        msg_style = (
            styles['mono'] if t.status == 'PASS' else
            ParagraphStyle(
                'msg_inline', parent=styles['mono'],
                textColor=_status_color(t.status),
                wordWrap='CJK',
            )
        )
        # escape para o nome (improvável conter < >, mas seguro)
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
        # header
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_HEADER),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 9),
        ('ALIGN',      (0, 0), (-1, 0), 'LEFT'),
        ('ALIGN',      (2, 0), (2, 0),  'RIGHT'),
        # body
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
        # Nome do teste já é Paragraph com seu próprio estilo Courier;
        # não aplicamos FONTNAME/FONTSIZE pra célula (1, i) aqui.
        if i % 2 == 0:
            cmds.append(('BACKGROUND', (0, i), (-1, i), COLOR_BG_ROW))
    table.setStyle(TableStyle(cmds))
    return table


def generate_unity_pdf(
    output_path: Path,
    test_file:   Path,
    mode:        str,
    summary:     UnitySummary,
    run_dt:      datetime | None = None,
) -> None:
    """
    Gera o PDF de relatório de testes Unity em output_path.

    output_path.parent é criado se não existir.
    """
    if run_dt is None:
        run_dt = datetime.now()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm,  bottomMargin=15*mm,
        title=f'tddl test report — {test_file.name}',
        author='tddl',
    )

    styles = _make_unity_styles()
    overall_label = 'OK' if summary.overall_ok else 'FAILED'
    overall_color = COLOR_PASS if summary.overall_ok else COLOR_FAIL
    overall_hex = '#' + overall_color.hexval()[2:]

    elements = [
        Paragraph('Unity Test Report', styles['title']),
        Paragraph(
            f'<font color="{overall_hex}"><b>{overall_label}</b></font> '
            f'— {summary.total} tests run, '
            f'{summary.failures} failed, '
            f'{summary.ignored} ignored',
            styles['subtitle'],
        ),
        _unity_metadata_table(test_file, mode, run_dt),
        Spacer(1, 4*mm),
        _unity_summary_cards(summary),
        Spacer(1, 6*mm),
        Paragraph('Test results', styles['section']),
    ]

    if summary.tests:
        elements.append(_unity_tests_table(summary.tests, styles))
    else:
        elements.append(Paragraph(
            '<i>No test results were parsed from the Unity output.</i>',
            styles['msg'],
        ))

    doc.build(elements)