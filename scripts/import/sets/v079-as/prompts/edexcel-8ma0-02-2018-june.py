from pathlib import Path
from lib import SHOW, SIG3, G, context
from native import read_questions

Q = read_questions(Path(__file__).with_suffix('.txt'))

CONTEXT = {n: context(SHOW, SIG3, G) if n >= 6 else context(SHOW, SIG3) for n in Q}
