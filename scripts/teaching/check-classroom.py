"""Exercise classroom controls at the published chapter routes and save per-slide observations.

Run against a locally served release candidate. JSONL files are private review
inputs. Re-read the slides and printed panels before assigning teaching approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Error, sync_playwright


REPO = Path(__file__).resolve().parents[2]
SNAPSHOT = """() => {
  const panel = document.querySelector('#slide-content');
  const visible = e => !!e.getClientRects().length && getComputedStyle(e).visibility === 'visible'
      && !e.closest('[aria-hidden=true],.is-hidden,.answer-concealed');
  const controls = [...panel.querySelectorAll('button,[role=button]')].filter(visible);
  return {
    controls: controls.map(e => ({key:e.dataset.shape || e.id || '',label:e.innerText.trim() || e.ariaLabel})),
    errors: panel.querySelectorAll('.katex-error').length,
    missingImages: [...panel.querySelectorAll('img')].filter(i => !i.complete || !i.naturalWidth).map(i => i.alt),
    oversizeText: [...panel.querySelectorAll('.lesson-image-tex')].filter(e => visible(e) &&
      (e.scrollWidth > e.clientWidth+4 || e.scrollHeight > e.clientHeight+4)).map(e => e.parentNode.dataset.shape),
    next: !document.querySelector('#next-step').disabled
  };
}"""


def frame(page):
    page.evaluate('new Promise(done=>requestAnimationFrame(()=>requestAnimationFrame(done)))')
    pixels = page.locator('#slide-region').screenshot(animations='disabled', type='jpeg', quality=63)
    return hashlib.sha256(pixels).hexdigest()


def inspect(page, index):
    page.evaluate('i=>FMQ_TEST.show(i)', index)
    page.evaluate('document.fonts.ready')
    page.evaluate('Promise.allSettled([...document.querySelectorAll("#slide-content img")].map(i=>i.decode()))')
    info = page.evaluate("""() => {
      const s=FMQ_TEST.getState().slide;
      return {id:s.id,title:s.title,covers:s.covers, triggers:Object.keys(s.animation?.triggers || {})};
    }""")
    initial = page.evaluate(SNAPSHOT)
    initial_hash = frame(page)
    physical = []
    for key in dict.fromkeys(info['covers'] + info['triggers']):
        page.evaluate('FMQ_TEST.reset()')
        selector = page.evaluate('id=>"[data-shape="+CSS.escape(id)+"]"', key)
        node = page.locator('#slide-content').locator(selector)
        if node.count() != 1 or not node.is_visible():
            physical.append([key, 'absent or initially hidden'])
            continue
        try:
            node.click(timeout=1200)
            physical.append([key, 'changed' if frame(page) != initial_hash else 'same board pixels'])
        except Error as error:
            physical.append([key, error.message.splitlines()[0]])
    page.evaluate('FMQ_TEST.reset();document.activeElement?.blur()')
    previous = frame(page)
    keyboard = []
    # A stalled control is recorded once. Very long intentional sequences are
    # flagged for inspection rather than counted as tested.
    for _ in range(120):
        if page.locator('#next-step').is_disabled():
            break
        page.keyboard.press('Space')
        current = frame(page)
        keyboard.append(current != previous)
        if current == previous:
            break
        previous = current
    after = page.evaluate(SNAPSHOT)
    page.locator('#reset').click()
    page.evaluate('document.activeElement?.blur()')
    return dict(number=index+1, **info, initial=initial, physical=physical, spaceChanged=keyboard,
                afterKeyboard=after, resetMatchesInitial=(frame(page)==initial_hash))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base_url')
    parser.add_argument('output', type=Path)
    parser.add_argument('--book', action='append')
    parser.add_argument('--chapter', type=int)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    data = (REPO/'teaching-catalogue.js').read_text().split('=',1)[1].strip().rstrip(';')
    catalogue = json.loads(data)
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(channel='chrome')
        for book, volume in reversed(catalogue.items()):
            if args.book and book not in args.book:
                continue
            for chapter in volume['chapters']:
                number = chapter['number']
                if args.chapter and args.chapter != number:
                    continue
                page = browser.new_page(viewport={'width':1440,'height':900},reduced_motion='reduce')
                target = args.output/f'{book}-{number}.jsonl'
                try:
                    page.goto(urljoin(args.base_url,chapter['slides']))
                    page.wait_for_function('window.FMQ_TEST?.getState()?.slide')
                    total = page.evaluate('FMQ_TEST.getState().deck.slides.length')
                    with target.open('w') as stream:
                        for index in range(total):
                            try:
                                row = inspect(page,index)
                            except Error as error:
                                row = dict(number=index+1, runnerError=error.message.splitlines()[0])
                            stream.write(json.dumps(row,ensure_ascii=False)+'\n')
                            stream.flush()
                    print(book,number,total,flush=True)
                finally:
                    page.close()
        browser.close()


if __name__ == '__main__':
    main()
