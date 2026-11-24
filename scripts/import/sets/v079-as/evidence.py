"""Verify the AS source pairs, printed marks and ordered scheme and figure assets."""
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import common

dataset = common.ImportSet(common.parser(__doc__, paper=False).parse_args())
papers = []
for pid, source in dataset.papers.items():
    dataset.pdf(pid, 'qp')
    dataset.pdf(pid, 'ms')
    assets = json.loads(dataset.assets_path(pid).read_text())
    payload = json.loads((dataset.repo / f'content/exams/{pid}.json').read_text())
    expected = dataset.data('marks.json')[pid]
    checks = []
    for n, (question, mark) in enumerate(zip(payload['questions'], expected, strict=True), 1):
        parts = [int(x) for x in re.findall(r'class="marks">\((\d+)\)', question['question'])]
        assert sum(parts) == mark, (pid, n, parts, mark)
        figures = assets['figures'].get(str(n), [])
        scheme = assets['markScheme'][str(n)]
        assert scheme and [x['asset'] for x in scheme] == re.findall(r'<img src="([^"]+)"', ''.join(question['steps']))
        assert [x['asset'] for x in figures] == re.findall(r'<img src="([^"]+)"', question['question'])
        for item in figures + scheme:
            assert hashlib.sha256((dataset.repo / item['asset']).read_bytes()).hexdigest() == item['sha256'], item['asset']
        checks.append(dict(number=n, marks=parts, schemePages=list(dict.fromkeys(x['sourcePage'] for x in scheme)),
                           schemeSegments=len(scheme), figures=len(figures)))
    papers.append(dict(paperId=pid, sourceHashes=assets['sourceHashes'], questions=checks))
evidence = dict(requirement='PAP-079-1', issue=145, papers=papers)
out = dataset.repo / 'docs/evidence/v079-official-as.json'
out.write_text(json.dumps(evidence, indent=1, ensure_ascii=False) + '\n')
print(f"Verified {len(papers)} source pairs or sections and {sum(len(p['questions']) for p in papers)} questions")
