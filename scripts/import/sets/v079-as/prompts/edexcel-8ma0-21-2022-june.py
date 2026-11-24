from pathlib import Path
from lib import SHOW, TABLES, INEXACT, context
from native import read_questions

CONTEXT = context(SHOW, TABLES, INEXACT)
Q = read_questions(Path(__file__).with_suffix('.txt'))
