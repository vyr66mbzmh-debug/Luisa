"""Access controls for the school's Further Mechanics 1 teaching resources."""
import re

BOOK = 'further-mechanics-1'
PREFIX = 'resources/teaching/v003/' + BOOK + '/'
TITLES = (
    'Momentum and impulse', 'Work, energy and power', 'Elastic strings and springs',
    'Elastic collisions in one dimension', 'Elastic collisions in two dimensions',
)


def teaching_catalogue(staff):
    chapters = []
    for number, title in enumerate(TITLES, 1):
        name = f'chapter-{number:02}.pdf'
        chapter = dict(number=number, title=title,
                       slides=f'teaching-lesson-viewer.html?book={BOOK}&chapter={number}&slide=1',
                       booklet=PREFIX + 'booklets/' + name, solutions=PREFIX + 'solutions/' + name)
        if staff:
            chapter['pdf'] = PREFIX + 'textbook/' + name
        chapters.append(chapter)
    return dict(title='Further Mechanics 1', chapters=chapters)


def permitted(name, staff):
    if staff and re.fullmatch(r'textbook/chapter-0[1-5]\.pdf', name):
        return True
    return bool(re.fullmatch(
        r'index\.json|chapter-0[1-5]\.json|assets/[a-f0-9]{20}\.(?:png|jpeg|svg)|'
        r'(?:booklets|solutions)/chapter-0[1-5]\.pdf', name))
