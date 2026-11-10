from pathlib import Path
import json
import re
from house_rule_links import make_converter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/7. House Rules'
OUTPUT = ROOT / 'house-rules'
BASE = '/SkroxiousDM'
files = sorted((p for p in SOURCE.rglob('*') if p.is_file() and p.suffix.lower() in ('.md', '.markdown')), key=lambda p: p.relative_to(SOURCE).as_posix().casefold())
if not files:
    raise SystemExit('No house-rule Markdown files found')

def slug(value):
    result = re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
    if not result:
        raise ValueError('Empty slug: ' + value)
    return result

routes, names, used = {}, {}, set()
for path in files:
    relative = path.relative_to(SOURCE).with_suffix('')
    route = '/house-rules/' + '/'.join(slug(part) for part in relative.parts) + '/'
    if route in used:
        raise ValueError('Duplicate house-rule route: ' + route)
    used.add(route)
    routes[path.resolve()] = route
    names.setdefault(path.stem.casefold(), []).append(path.resolve())
_, convert = make_converter(ROOT, SOURCE, BASE, routes, names)

def page(title, route, body):
    return '---\nlayout: default\ntitle: ' + json.dumps(title, ensure_ascii=False) + '\npermalink: ' + route + '\n---\n' + body

OUTPUT.mkdir(parents=True, exist_ok=True)
index = ['[Back to campaign reference](' + BASE + '/campaign/)\n', '> House-rule reference. Confirm with your GM which rules apply.\n', '## All house rules\n']
for path in files:
    route = routes[path.resolve()]
    text = path.read_text(encoding='utf-8-sig')
    text = re.sub(r'\A---\r?\n.*?\r?\n---\r?\n', '', text, count=1, flags=re.S)
    if '{% endraw %}' in text:
        raise ValueError('Unsupported Liquid endraw in ' + str(path))
    text = convert(text, path)
    body = '[House rules index](' + BASE + '/house-rules/) | [Campaign reference](' + BASE + '/campaign/)\n\n{% raw %}\n' + text + '\n{% endraw %}\n'
    destination = ROOT / route.strip('/') / 'index.md'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page(re.sub(r'[_-]+', ' ', path.stem), route, body), encoding='utf-8')
    label = path.relative_to(SOURCE).with_suffix('').as_posix().replace('_', ' ')
    index.append('- [' + label + '](' + BASE + route + ')\n')
(OUTPUT / 'index.md').write_text(page('House Rules', '/house-rules/', '\n'.join(index)), encoding='utf-8')
print('Generated', len(files), 'house-rule pages plus the complete index')
