"""Small WSGI path-prefix adapter for ADA's /AL/ deployment."""


class PrefixMiddleware:
    """Mount the application at /AL without allowing requests outside its prefix."""
    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix.rstrip('/')
        if self.prefix and (not self.prefix.startswith('/') or '..' in self.prefix.split('/')):
            raise RuntimeError('LUISA_URL_PREFIX must be a normalized path such as /AL')

    def __call__(self, environ, start_response):
        if not self.prefix:
            return self.app(environ, start_response)
        path = environ.get('PATH_INFO', '/')
        current_script = environ.get('SCRIPT_NAME', '')
        if current_script == self.prefix:
            return self.app(environ, start_response)
        if path == self.prefix or path.startswith(self.prefix + '/'):
            environ['SCRIPT_NAME'] = current_script + self.prefix
            environ['PATH_INFO'] = path[len(self.prefix):] or '/'
            return self.app(environ, start_response)
        start_response('404 Not Found', [('Content-Type', 'text/plain; charset=utf-8'), ('Cache-Control', 'no-store')])
        return [b'Not found']
