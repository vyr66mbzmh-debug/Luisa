from pathlib import Path
from lib import SHOW, SIG3, context
from native import read_questions

CONTEXT = context(SHOW, SIG3)
Q = read_questions(Path(__file__).with_suffix('.txt'))
