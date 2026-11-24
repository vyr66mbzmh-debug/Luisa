"""Official AS paper and scheme sources, including separately numbered specimen sections."""
import json
from pathlib import Path

PAPERS = json.loads(Path(__file__).with_name('sources.json').read_text())
ORDER = sorted(PAPERS, key=lambda key: (PAPERS[key]['series'] or '', key), reverse=True)
