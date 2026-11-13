"""Gunicorn entry point: serve only behind the ADA HTTPS reverse proxy."""
import os

from student_server.app import create_app
from student_server.middleware import PrefixMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix


# Trust exactly one upstream proxy only for the scheme. Nginx must overwrite
# X-Forwarded-Proto and must not expose Gunicorn outside loopback.
application = PrefixMiddleware(ProxyFix(create_app(), x_for=0, x_proto=1, x_host=0, x_port=0, x_prefix=0),
                               os.environ.get('LUISA_URL_PREFIX', ''))
