"""Regression coverage for deploying the same site below a plain-server prefix."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import urljoin, urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        self.urls.extend(value for key, value in attrs
                         if key in ('href', 'src', 'action') and value)


class SubpathAcceptance(unittest.TestCase):
    def test_static_entry_links_work_below_AL_OPS_002(self):
        count = 0
        for page in ROOT.glob('*.html'):
            parser = Links()
            parser.feed(page.read_text())
            for url in parser.urls:
                parsed = urlsplit(url)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                with self.subTest(page=page.name, url=url):
                    resolved = urlsplit(urljoin('https://example.test/AL/' + page.name, url)).path
                    self.assertTrue(resolved.startswith('/AL/'), resolved)
                    target = ROOT / unquote(resolved[len('/AL/'):])
                    # ADA has no Cloudflare clean-URL fallback.
                    self.assertTrue(target.is_file() or target.is_dir(), str(target))
                    count += 1
        self.assertGreater(count, 100)

    def test_release_cache_fetches_fresh_assets_OPS_002(self):
        self.assertIn('new Request(url,{cache:"reload"})', (ROOT / 'sw.js').read_text())

    def test_textbook_return_links_keep_prefix_OPS_002(self):
        source = (ROOT / 'textbook-view.js').read_text()
        for name in ('skillURL', 'bookURL'):
            body = re.search(r'function ' + name + r'\([^)]*\)\{([^\n]+)', source).group(1)
            prefix = re.search(r"return '([^']*)'\+hash", body).group(1)
            self.assertEqual(urlsplit(urljoin('https://example.test/AL/textbook-view.html', prefix + '#course=test')).path, '/AL/')

    def test_generated_lesson_return_links_keep_prefix_OPS_002(self):
        for name in ('lesson-viewer.js', 'lesson-source-viewer.js'):
            source = (ROOT / name).read_text()
            for url in re.findall(r'href=`([^`]+)`', source):
                if '#course=' in url:
                    self.assertEqual(urlsplit(urljoin('https://example.test/AL/viewer.html', url)).path,
                                     '/AL/')


if __name__ == '__main__':
    unittest.main()
