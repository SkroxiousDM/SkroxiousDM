from urllib.parse import unquote, urlsplit, urlunsplit
import re

LEGACY = '/SkroxiousDM'
LEGACY_HOST = 'skroxiousdm.github.io'

def read_site_config(path):
    text = path.read_text(encoding='utf-8')
    def scalar(name, default):
        match = re.search(r'^' + name + r':[ \t]*(?:"([^"\r\n]*)"|\x27([^\x27\r\n]*)\x27|([^#\r\n]*))', text, re.M)
        return next((value for value in match.groups() if value is not None), default).strip() if match else default
    url = scalar('url', 'https://skroxiousdm.github.io').rstrip('/')
    base = scalar('baseurl', '').rstrip('/')
    if base and not base.startswith('/'):
        raise ValueError('baseurl must be empty or begin with /')
    return url, base

class SitePaths:
    def __init__(self, base, site_url, routes):
        self.base = base
        self.host = urlsplit(site_url).netloc.casefold()
        self.routes = set(routes.values()) | {'/house-rules/', '/campaign/'}

    def to_site(self, target):
        parsed = urlsplit(target)
        if parsed.netloc and parsed.netloc.casefold() != LEGACY_HOST:
            return target
        if not parsed.path.startswith(LEGACY + '/'):
            return target
        route = unquote(parsed.path[len(LEGACY):])
        if route not in self.routes:
            return target
        return urlunsplit(('', '', self.base + route, parsed.query, parsed.fragment))

    def to_legacy(self, target):
        parsed = urlsplit(target)
        if not parsed.netloc or parsed.netloc.casefold() != self.host or self.host == LEGACY_HOST:
            return target
        path = unquote(parsed.path)
        if self.base:
            if not path.startswith(self.base + '/'):
                return target
            path = path[len(self.base):]
        if path.startswith(('/7. House Rules/', '/docs/7. House Rules/')):
            return urlunsplit(('https', LEGACY_HOST, LEGACY + path, parsed.query, parsed.fragment))
        return target

def make_converter(root, source, base, routes, names, site_url='https://skroxiousdm.github.io'):
    from house_rule_links import make_converter as legacy_factory, LINK, REFERENCE, INLINE_CODE, protected_lines
    legacy_resolve, legacy_convert = legacy_factory(root, source, LEGACY, routes, names)
    paths = SitePaths(base, site_url, routes)

    def rewrite(text, function):
        def destination(value):
            return '<' + function(value[1:-1]) + '>' if value.startswith('<') and value.endswith('>') else function(value)
        def segment(value):
            return LINK.sub(lambda m: m[1] + destination(m[2]) + (m[3] or '') + m[4], value)
        result = []
        for line, protected in protected_lines(text):
            if protected:
                result.append(line)
                continue
            ref = REFERENCE.match(line.rstrip('\r\n'))
            if ref:
                ending = '\r\n' if line.endswith('\r\n') else '\n' if line.endswith('\n') else ''
                result.append(ref[1] + destination(ref[2]) + ref[3] + ending)
                continue
            parts, offset = [], 0
            for code in INLINE_CODE.finditer(line):
                parts.extend([segment(line[offset:code.start()]), code[0]])
                offset = code.end()
            parts.append(segment(line[offset:]))
            result.append(''.join(parts))
        return ''.join(result)

    def resolve(target, current):
        return paths.to_site(legacy_resolve(paths.to_legacy(target), current))

    def convert(text, current):
        prepared = rewrite(text, paths.to_legacy)
        return rewrite(legacy_convert(prepared, current), paths.to_site)

    return resolve, convert
