import json
from pathlib import Path
from lib import SHOW, INEXACT, context, fig
CONTEXT = context(SHOW, INEXACT)
Q = {int(n): text for n, text in json.loads(Path(__file__).with_suffix('.json').read_text()).items()}
Q[5] = Q[5].replace('{figure}', fig(5, 95, 'Figure 1. Shaded annulus on the Argand diagram.'))
Q[9] = Q[9].replace('{figure}', fig(9, 90, 'Figure 2. Vertical cross-section AOBCDE through the centre of a wax candle.'))
