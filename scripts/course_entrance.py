"""Keep historical A Level URLs at the site root when packaging the Cloudflare edition."""
import re


def owner_page(name, content):
    if name == 'courses/index.html':
        return 'index.html', content
    if name == 'app-navigation.js':
        # Keep the native Teaching Resources logo and destination in installed windows.
        content = content.replace(b"if(standalone()&&/(?:lesson|native)-viewer", b"if(!document.getElementById('library')&&standalone()&&/(?:lesson|native)-viewer")
    if name == 'lesson-viewer.js':
        content = re.sub(rb"\$\('library'\)\.href=[^;]+;", b'', content)
    if name == 'document-viewer.html':
        content = content.replace(b'\xe2\x86\x90 Back to Luisa</a>', b'<img src="assets/luisa/logo.png" width="84" alt="Luisa"></a>')
    if name in {'index.html', 'teaching-chapters.html', 'papers.html', 'textbook-view.html', 'offline.html'}:
        content = re.sub(rb'(<a\b[^>]*?href=")\./("[^>]*>By skill</a>)', rb'\g<1>by-skill.html\2', content)
        content = re.sub(rb'(?:<a [^>]+>)?(<img class="luisa-logo"[^>]+>)(?:</a>)?',
                         rb'<a href="./" aria-label="Home">\1</a>', content, count=1)
    if name == 'teaching-chapters.html':
        content = content.replace(b'<html lang="en">', b'<html lang="en" data-course-entrance>', 1)
    return ('by-skill.html' if name == 'index.html' else name), content
