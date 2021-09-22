from urllib.parse import urlparse

from envyaml import EnvYAML

HEADER_NAME = 'Content-Security-Policy'

KEYWORDS = (
    'none',
    'report-sample',
    'self',
    'strict-dynamic',
    'unsafe-eval',
    'unsafe-hashes',
    'unsafe-inline',
)

DEFAULT_PORTS = {
    "ftp": 21,
    "gopher": 70,
    "http": 80,
    "https": 443,
    "news": 119,
    "nntp": 119,
    "snews": 563,
    "snntp": 563,
    "telnet": 23,
    "ws": 80,
    "wss": 443,
}

def serialize_csp(input_path, strict=True,
                  minify=True, normalize_ports=False,
                  nginx_format=False):
    csp_object = EnvYAML(input_path, strict=strict)
    directives = csp_object[HEADER_NAME]

    def directives_generator():
        for directive, sources in directives.items():
            if refined_sources := tuple(filter(bool, (format_src(src, normalize_ports) for src in sources))):
                yield f'''{directive} {' '.join(refined_sources)}'''

    delimiter = ';' if minify else '; '
    csp_value = delimiter.join(directives_generator())

    if not minify:
        csp_value += ';'

    if nginx_format:
        return f'add_header {HEADER_NAME} "{csp_value}";'

    return csp_value

def format_src(src, normalize_ports=False):
    src = str(src or '').strip('\'"')

    if src in KEYWORDS:
        return f"'{src}'"

    if normalize_ports:
        src = normalize_port(src)

    return src

def normalize_port(src):
    parsed = urlparse(src)

    try:
        port = parsed.port
    except ValueError:
        return src

    if port is None or port != DEFAULT_PORTS.get(parsed.scheme.lower(), None):
        return src

    netloc = parsed.netloc.rsplit(':', 1)[0]
    # noinspection PyProtectedMember
    return parsed._replace(netloc=netloc).geturl()
