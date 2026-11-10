from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit, quote
import re
import shutil

RESERVED = {'action', 'attack', 'movement', 'reaction', 'opportunity', 'superiority'}
LINK = re.compile(r'(!?\[[^\]\n]*\]\()(<[^>\n]*>|(?:\\.|[^\s()\\]|\([^()\n]*\))+)([ \t]+(?:"[^"\n]*"|\x27[^\x27\n]*\x27|\([^()\n]*\)))?([ \t]*\))')
REFERENCE = re.compile(r'^( {0,3}\[[^\]\n]+\]:[ \t]*)(<[^>\n]*>|\S+)(.*)$')
INLINE_CODE = re.compile(r'(`+)(.*?)\1', re.S)

def key(value):
    return re.sub(r'\s+', ' ', value.replace('\u200b', '').strip()).casefold()

def protected_lines(text):
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line.rstrip('\r\n'))
        if fence:
            yield line, True
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
        elif marker:
            fence = (marker[1][0], len(marker[1]))
            yield line, True
        else:
            yield line, line.startswith(('    ', '\t'))

def heading_rows(text):
    used = {}
    rows = []
    for line, protected in protected_lines(text):
        match = re.match(r'^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$', line)
        if match and not protected:
            label = match[1].replace('\u200b', '')
            stem = re.sub(r'[^a-z0-9]+', '-', label.casefold()).strip('-') or 'section'
            count = used.get(stem, 0)
            used[stem] = count + 1
            rows.append((key(label), 'hr-' + stem + ('-' + str(count) if count else '')))
    return rows

def make_converter(root, source, base, routes, names):
    root, source = root.resolve(), source.resolve()
    headings = {}
    for path in routes:
        entries = {}
        for label, anchor in heading_rows(path.read_text(encoding='utf-8-sig')):
            entries.setdefault(label, []).append(anchor)
        headings[path] = entries
    condition_files = names.get('conditions', [])
    conditions = condition_files[0] if len(condition_files) == 1 else None

    def resolve(target, current):
        parsed = urlsplit(target)
        if not target or target.startswith('#') or parsed.scheme not in ('', 'http', 'https'):
            return target
        path = unquote(parsed.path)
        if not parsed.netloc and path in {base + route for route in routes.values()}:
            return target
        if parsed.netloc and (parsed.netloc.casefold() != 'skroxiousdm.github.io' or not path.startswith(base + '/')):
            return target
        if path.startswith(base + '/'):
            relative = path[len(base) + 1:]
            candidates = [root / relative]
            if relative.startswith('7. House Rules/'):
                candidates.append(root / 'docs' / relative)
        elif path.startswith('/'):
            return target
        else:
            candidates = [current.parent / path, source / path]
        expanded = []
        for candidate in candidates:
            expanded.append(candidate.resolve())
            if candidate.suffix.lower() not in ('.md', '.markdown'):
                expanded.extend(Path(str(candidate) + ext).resolve() for ext in ('.md', '.markdown'))
        found = next((p for p in expanded if p in routes), None)
        if found is None and '/' not in path and '\\' not in path:
            matches = names.get(Path(path).stem.casefold(), [])
            if len(matches) == 1:
                found = matches[0]
        if found:
            return urlunsplit(('', '', base + routes[found], parsed.query, parsed.fragment))
        for candidate in expanded:
            if candidate.is_file() and candidate.is_relative_to(source) and candidate.suffix.lower() not in ('.md', '.markdown'):
                relative = candidate.relative_to(source)
                destination = root / 'assets/house-rules' / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(candidate, destination)
                return urlunsplit(('', '', base + '/assets/house-rules/' + quote(relative.as_posix(), safe='/'), parsed.query, parsed.fragment))
        for candidate in expanded:
            if candidate.is_file() and candidate.is_relative_to(root):
                relative = quote(candidate.relative_to(root).as_posix(), safe='/')
                return urlunsplit(('https', 'github.com', '/SkroxiousDM/SkroxiousDM/blob/main/' + relative, parsed.query, parsed.fragment))
        if not parsed.netloc:
            print('Unresolved link:', current.relative_to(source), target)
        return target

    def bare_url(label, current):
        normalized = key(label)
        if normalized in RESERVED:
            return None
        for candidate in dict.fromkeys([current, conditions]):
            anchors = headings.get(candidate, {}).get(normalized, [])
            if len(anchors) == 1:
                return base + routes[candidate] + '#' + anchors[0]
        matches = names.get(normalized, [])
        return base + routes[matches[0]] if len(matches) == 1 else None

    def convert(text, current):
        definitions = set()
        for line, protected in protected_lines(text):
            match = REFERENCE.match(line.rstrip('\r\n'))
            if match and not protected:
                definitions.add(key(re.search(r'\[([^]]+)\]', match[1])[1]))
        stored = []
        def hold(value):
            marker = '\x00HR' + str(len(stored)) + '\x00'
            stored.append(value)
            return marker
        def destination(value):
            if value.startswith('<') and value.endswith('>'):
                return '<' + resolve(value[1:-1], current) + '>'
            return resolve(value, current)
        def rewrite_segment(segment):
            def wiki(match):
                target, separator, label = match[2].partition('|')
                resolved = resolve(target, current)
                if resolved == target or match[1]:
                    return hold(match[0])
                return hold('[' + (label if separator else Path(target.split('#')[0]).stem) + '](' + resolved + ')')
            segment = re.sub(r'(!?)\[\[([^\]]+)\]\]', wiki, segment)
            segment = LINK.sub(lambda m: hold(m[1] + destination(m[2]) + (m[3] or '') + m[4]), segment)
            segment = re.sub(r'!?\[([^]\n]+)\]\[([^]\n]*)\]', lambda m: hold(m[0]), segment)
            def bare(match):
                if key(match[1]) in definitions:
                    return match[0]
                url = bare_url(match[1], current)
                return '[' + match[1] + '](' + url + ')' if url else match[0]
            return re.sub(r'(?<![!\\\[])\[([^]\n]+)\](?![\[(])', bare, segment)
        lines = []
        anchors = iter(heading_rows(text))
        for line, protected in protected_lines(text):
            if protected:
                lines.append(line)
                continue
            ref = REFERENCE.match(line.rstrip('\r\n'))
            if ref:
                ending = '\n' if line.endswith('\n') else ''
                lines.append(ref[1] + destination(ref[2]) + ref[3] + ending)
                continue
            if re.match(r'^ {0,3}#{1,6}\s+', line):
                _, anchor = next(anchors)
                lines.append('<a id="' + anchor + '"></a>\n\n' + line)
                continue
            parts, position = [], 0
            for code in INLINE_CODE.finditer(line):
                parts.append(rewrite_segment(line[position:code.start()]))
                parts.append(hold(code[0]))
                position = code.end()
            parts.append(rewrite_segment(line[position:]))
            lines.append(''.join(parts))
        result = ''.join(lines)
        for i, value in enumerate(stored):
            result = result.replace('\x00HR' + str(i) + '\x00', value)
        return result
    return resolve, convert
