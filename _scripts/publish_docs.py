from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit, quote
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = 'Curse-of-Strahd-Reloaded-main'
DEFERRED = 'Arc_S-A_Sword_of_Sunlight.md'
SECTIONS = {
    '1. Start Here': ('/reference/start-here/', 'Start Here'),
    '2. Origins': ('/reference/origins/', 'Origins'),
    '3.Classes': ('/reference/classes/', 'Classes'),
    '4.Feats': ('/reference/feats/', 'Feats'),
    '5.Equipment': ('/reference/equipment/', 'Equipment'),
    '6.Spells': ('/reference/spells/', 'Spells'),
    '7. House Rules': ('/house-rules/', 'House Rules'),
    'RoS-CoS-RRL': ('/campaign/chronicle/', 'Characters and Recaps'),
    'simple-quest': ('/campaign/quests-and-lore/', 'Quests and Lore'),
}

def excluded(relative):
    return relative.parts[0] == EXCLUDED or relative.name == DEFERRED

def slug(value):
    result = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    if not result:
        raise ValueError('Empty route component: ' + value)
    return result

def route_for(relative):
    prefix, _ = SECTIONS.get(relative.parts[0], ('/reference/', 'Other Documents'))
    parts = relative.parts[1:] if relative.parts[0] in SECTIONS else relative.parts
    if relative.as_posix().casefold() == 'index.md':
        return '/reference/overview/'
    return prefix + '/'.join(slug(part) for part in Path(*parts).with_suffix('').parts) + '/'

def plan(source):
    routes, names, used = {}, {}, set(['/reference/'] + [v[0] for v in SECTIONS.values()])
    for path in sorted(source.rglob('*'), key=lambda p: p.as_posix().casefold()):
        relative = path.relative_to(source)
        if not path.is_file() or path.is_symlink() or excluded(relative) or path.suffix.lower() not in ('.md', '.markdown'):
            continue
        route = route_for(relative)
        if route in used:
            raise ValueError('Duplicate or reserved route: ' + route)
        used.add(route)
        routes[path.resolve()] = route
        names.setdefault(path.stem.casefold(), []).append(path.resolve())
    return routes, names

def page(title, route, body):
    return '---\nlayout: default\ntitle: ' + json.dumps(title, ensure_ascii=False) + '\npermalink: ' + route + '\n---\n' + body

def rewrite_links(text, function):
    from house_rule_links import LINK, REFERENCE, INLINE_CODE, protected_lines
    def dest(value):
        return '<' + function(value[1:-1]) + '>' if value.startswith('<') and value.endswith('>') else function(value)
    def segment(value):
        return LINK.sub(lambda m: m[1] + dest(m[2]) + (m[3] or '') + m[4], value)
    result = []
    for line, protected in protected_lines(text):
        if protected:
            result.append(line)
            continue
        ref = REFERENCE.match(line.rstrip('\r\n'))
        if ref:
            result.append(ref[1] + dest(ref[2]) + ref[3] + ('\n' if line.endswith('\n') else ''))
            continue
        parts, offset = [], 0
        for code in INLINE_CODE.finditer(line):
            parts.extend([segment(line[offset:code.start()]), code[0]])
            offset = code.end()
        parts.append(segment(line[offset:]))
        result.append(''.join(parts))
    return ''.join(result)

def main():
    from site_links import make_converter, read_site_config
    source = ROOT / 'docs'
    site_url, base = read_site_config(ROOT / '_config.yml')
    routes, names = plan(source)
    if not routes:
        raise SystemExit('No publishable Markdown files found')
    _, convert = make_converter(ROOT, source, base, routes, names, site_url=site_url)
    aliases = {}
    for path, route in routes.items():
        relative = path.relative_to(source).as_posix()
        for alias in (relative, str(Path(relative).with_suffix('')), str(Path(relative).with_suffix('.html'))):
            aliases[alias] = route
            aliases['docs/' + alias] = route
    assets = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.avif', '.pdf', '.mp3', '.mp4', '.ogg', '.wav'}
    def normalize(target, current):
        parsed = urlsplit(target)
        if parsed.scheme not in ('', 'http', 'https') or not parsed.path:
            return target
        path = unquote(parsed.path)
        host = parsed.netloc.casefold()
        legacy = host == 'skroxiousdm.github.io'
        if host and host not in ('skroxiousdm.github.io', urlsplit(site_url).netloc.casefold()):
            return target
        if legacy and not path.startswith('/SkroxiousDM/'):
            return target
        if path.startswith('/SkroxiousDM/'):
            path = path[len('/SkroxiousDM/'):]
        elif base and path.startswith(base + '/'):
            path = path[len(base) + 1:]
        else:
            path = path.lstrip('/')
        route = aliases.get(path.rstrip('/')) if host or parsed.path.startswith('/') else None
        if route:
            return urlunsplit(('', '', base + route, parsed.query, parsed.fragment))
        if Path(path).suffix.lower() in assets:
            candidates = [source / path, ROOT / path] if host or parsed.path.startswith('/') else [current.parent / unquote(parsed.path), source / path, ROOT / path]
            for candidate in candidates:
                candidate = candidate.resolve()
                if not candidate.is_file() or not candidate.is_relative_to(ROOT):
                    continue
                relative = candidate.relative_to(ROOT)
                if candidate.is_relative_to(source) and excluded(candidate.relative_to(source)):
                    return target
                destination = ROOT / 'assets/reference' / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(candidate, destination)
                return urlunsplit(('', '', base + '/assets/reference/' + quote(relative.as_posix(), safe='/'), parsed.query, parsed.fragment))
        return target
    groups = {}
    def write(title, route, body):
        destination = ROOT / route.strip('/') / 'index.md'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(page(title, route, body), encoding='utf-8')
    for path, route in routes.items():
        relative = path.relative_to(source)
        section = relative.parts[0]
        prefix, title = SECTIONS.get(section, ('/reference/', 'Other Documents'))
        text = path.read_text(encoding='utf-8-sig')
        text = re.sub(r'\A---\r?\n.*?\r?\n---\r?\n', '', text, count=1, flags=re.S)
        if '{% endraw %}' in text:
            raise ValueError('Unsupported Liquid endraw in ' + str(path))
        text = rewrite_links(text, lambda value: normalize(value, path))
        text = convert(text, path)
        label = re.sub(r'[_-]+', ' ', path.stem)
        navigation = '[Reference library](' + base + '/reference/) | [' + title + '](' + base + prefix + ') | [Campaign](' + base + '/campaign/)\n\n'
        if prefix.startswith('/campaign/'):
            navigation += '> Campaign notes: may contain spoilers.\n\n'
        write(label, route, navigation + '{% raw %}\n' + text + '\n{% endraw %}\n')
        groups.setdefault(section if section in SECTIONS else '', []).append((relative.as_posix(), route))
    landing = ['[Campaign reference](' + base + '/campaign/)\n', 'Original Markdown notes are preserved; these web editions are generated during the build.\n']
    for section, entries in groups.items():
        prefix, title = SECTIONS.get(section, ('/reference/', 'Other Documents'))
        listing = ['- [' + label.replace('[', r'\[').replace(']', r'\]') + '](' + base + route + ')' for label, route in entries]
        if prefix != '/reference/':
            write(title, prefix, '[Reference library](' + base + '/reference/)\n\n' + ('> Campaign notes may contain spoilers.\n\n' if prefix.startswith('/campaign/') else '') + '\n'.join(listing) + '\n')
            landing.append('## [' + title + '](' + base + prefix + ')\n')
        else:
            landing.append('## Other Documents\n')
        landing.extend(listing)
        landing.append('')
    write('Reference Library', '/reference/', '\n'.join(landing))
    print('Generated', len(routes), 'Markdown web editions with section indexes; Strahd archive excluded')

if __name__ == '__main__':
    main()
