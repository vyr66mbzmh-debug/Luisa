"""HTML helpers for past-paper prompt files (sets/<name>/prompts/<paperId>.py use `from lib import *`)."""
import html

ASSETS = {}
def load(record):
    """Use one paper's asset record (written by build_assets.py)."""
    ASSETS.clear(); ASSETS.update(record)
def m(tex): return f'<span class="inline-math" data-math="{html.escape(tex, quote=True)}"></span>'
def eq(tex): return f'<div class="equation" data-math="{html.escape(tex, quote=True)}" data-display="true"></div>'
def mk(n): return f'<span class="marks">({n})</span>'
def parts(items, start=1, kind=None):
    attrs = (f' type="{kind}"' if kind else '') + (f' start="{start}"' if start != 1 else '')
    return f'<ol class="parts"{attrs}>' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'
def ul(items): return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
def p(text): return f'<p>{text}</p>'
def bold(text): return f'<p><strong>{text}</strong></p>'
def fig(n, width, alt, k=1):
    a = ASSETS['figures'][str(n)][k - 1]
    return (f'<figure class="practice-figure" style="max-width:{width}mm;margin:2mm auto"><img src="{a["asset"]}" '
            f'alt="{html.escape(alt, quote=True)}"></figure>')
def table(rows, head=0):
    out = '<table class="practice-table">'
    for i, r in enumerate(rows):
        tag = 'th' if i < head else 'td'
        out += '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in r) + '</tr>'
    return out + '</table>'
def context(*lines):
    return ('<aside class="exam-instructions"><p><strong>Original paper instructions</strong></p>'
            + ''.join(f'<p>{l}</p>' for l in lines) + '</aside>')
SHOW = 'You should show sufficient working to make your methods clear. Answers without working may not gain full credit.'
INEXACT = 'Inexact answers should be given to three significant figures unless otherwise stated.'
TABLES = 'Values from statistical tables should be quoted in full. If a calculator is used instead of tables the value should be given to an equivalent degree of accuracy.'
G = ('Unless otherwise indicated, whenever a value of ' + m('g') + ' is required, take ' + m(r'g=9.8\,\mathrm{m}\,\mathrm{s}^{-2}')
     + ' and give your answer to either 2 significant figures or 3 significant figures.')
ALL_STAGES = bold('In this question you must show all stages of your working.')
NO_CALC = bold('Solutions relying on calculator technology are not acceptable.')
NO_CALC_ENTIRELY = bold('Solutions relying entirely on calculator technology are not acceptable.')
DETAILED = bold('In this question you must show detailed reasoning.')
SIG3 = 'Answers should be given to three significant figures unless otherwise stated.'
