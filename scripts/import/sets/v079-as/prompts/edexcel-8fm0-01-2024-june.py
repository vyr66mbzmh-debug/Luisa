from pathlib import Path
from lib import SHOW, INEXACT, context
from native import read_questions

CONTEXT = context(SHOW, INEXACT)
Q = read_questions(Path(__file__).with_suffix('.txt'))
