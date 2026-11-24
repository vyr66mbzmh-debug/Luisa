"""Join reviewed AS question skills to Luisa's existing Year 1 topics."""
import json
from pathlib import Path

SET = Path(__file__).parent
ROOT = SET.parents[3]
library = json.loads((ROOT / 'data.js').read_text().removeprefix('window.FMQ_LIBRARY=').rstrip(';\n'))
titles = {s['id']: s['title'] for course in library['courses'] for book in course['books']
          for topic in book['topics'] for s in topic['skills']}
textbook = json.loads((ROOT / 'textbook-catalogue.json').read_text())
targets = {}
for question in textbook['questions']:
    for target in question['targets']:
        book = target['book']
        if book == 'pure-core-1' or book.endswith('-year-1'):
            chapter = f"{book}/{target['chapter']}"
            ordered = targets.setdefault(question['skill'], [])
            if chapter not in ordered:
                ordered.append(chapter)
MAPS = {}
for paper, questions in json.loads((SET / 'skills.json').read_text()).items():
    by_number = MAPS[paper] = {}
    for number, numbers in enumerate(questions, 1):
        prefix = '1.' if '8fm0' in paper else 'smq-1.'
        skills = [prefix + n for n in numbers.split()]
        chapters = list(dict.fromkeys(ch for skill in skills for ch in targets.get(skill, [])))
        if not chapters:
            raise ValueError((paper, number, skills))
        by_number[number] = (', '.join(titles[skill] for skill in skills), skills, chapters)
