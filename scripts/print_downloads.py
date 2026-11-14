"""Publish print-toolbar documents under descriptive, stable download names."""
import hashlib
import json
import os


def prepare_print_downloads(directory, entries):
    catalogue = directory / 'data.js'
    if not catalogue.exists():
        return
    library = json.loads(catalogue.read_text().split('=', 1)[1].strip().rstrip(';'))
    names = {}
    for course in library['courses']:
        maths = course['id'] == 'maths-a-level'
        for book in course['books']:
            for topic in book['topics']:
                title = ' '.join(('Maths' if maths else 'FM', book['title'], topic['title']))
                topic_pdf = topic.get('printoutPath' if maths else 'edexcelPrintoutPath')
                documents = [(topic_pdf, title)]
                for skill in topic['skills']:
                    code = skill['code']
                    revision = 'v03' if code == '1.28' else 'v02'
                    skill_pdf = skill.get('printoutPath') if maths else f"printouts/{book['id']}/{topic['id']}/skills/{skill['id']}_{revision}.pdf"
                    documents.append((skill_pdf, f'{title} {code}'))
                    documents.append((skill.get('solutionsResource'), f'{title} {code} SOLUTIONS'))
                for source, name in documents:
                    if not source:
                        continue
                    if any(c in name for c in '/\\?#'):
                        raise ValueError(f'Invalid PDF filename: {name}')
                    alias = f'printouts/named/{name}.pdf'
                    if alias in entries or source in names:
                        raise ValueError(f'Ambiguous print destination: {alias}')
                    target = directory / alias
                    target.parent.mkdir(exist_ok=True, parents=True)
                    os.link(directory / source, target)
                    entries[alias] = entries[source].copy()
                    names[source] = alias
    library['printDownloads'] = names
    content = ('window.FMQ_LIBRARY=' + json.dumps(library, ensure_ascii=False, separators=(',', ':')) + ';\n').encode()
    catalogue.write_bytes(content)
    entries['data.js'] = {'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
