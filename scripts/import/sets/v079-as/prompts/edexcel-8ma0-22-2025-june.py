from pathlib import Path
from lib import SHOW, G, context
from native import read_questions

CONTEXT = context(SHOW, G)
Q = read_questions(Path(__file__).with_suffix('.txt'))
