import tempfile
import unittest
from pathlib import Path
from house_rule_links import make_converter

ROUTE = '/SkroxiousDM/house-rules/conditions/'
CASES = [
    ('Relative Markdown', '[Conditions](Conditions.md)', '[Conditions](' + ROUTE + ')'),
    ('Reference definition', '[conditions]: Conditions.md', '[conditions]: ' + ROUTE),
    ('Angle destination', '[Conditions](<Conditions.md>)', '[Conditions](<' + ROUTE + '>)'),
    ('Double quoted title', '[Conditions](Conditions.md "Condition rules")', '[Conditions](' + ROUTE + ' "Condition rules")'),
    ('Single quoted title', "[Conditions](Conditions.md 'Condition rules')", "[Conditions](" + ROUTE + " 'Condition rules')"),
    ('Inline code', '`[Conditions](Conditions.md)`', '`[Conditions](Conditions.md)`'),
    ('Double backtick code', '``[Conditions](Conditions.md)``', '``[Conditions](Conditions.md)``'),
    ('Other repo', '[Other](https://skroxiousdm.github.io/Other/Conditions)', '[Other](https://skroxiousdm.github.io/Other/Conditions)'),
    ('Query and fragment', '[Conditions](Conditions.md?view=full#prone)', '[Conditions](' + ROUTE + '?view=full#prone)'),
    ('Condition shorthand', '[Prone]', '[Prone](' + ROUTE + '#hr-prone)'),
    ('Reserved labels', '[Action] [Attack] [Reaction]', '[Action] [Attack] [Reaction]'),
    ('Unknown reference', '[Unspecified]', '[Unspecified]'),
    ('Existing reference priority', '[Prone]\n\n[Prone]: https://example.org/', '[Prone]\n\n[Prone]: https://example.org/'),
    ('Full reference', '[Condition rules][conditions]\n\n[conditions]: Conditions.md', '[Condition rules][conditions]\n\n[conditions]: ' + ROUTE),
    ('Wiki alias', '[[Conditions|condition rules]]', '[condition rules](' + ROUTE + ')'),
    ('Fenced code', '```md\n[Conditions](Conditions.md)\n```', '```md\n[Conditions](Conditions.md)\n```'),
    ('Indented code', '    [Conditions](Conditions.md)', '    [Conditions](Conditions.md)'),
    ('Legacy URL', '[Conditions](https://skroxiousdm.github.io/SkroxiousDM/7.%20House%20Rules/Conditions)', '[Conditions](' + ROUTE + ')'),
    ('Nested page', '[Group](Nested/Group%20Checks.md)', '[Group](/SkroxiousDM/house-rules/nested/group-checks/)'),
    ('Other host', '[Conditions](https://example.com/Conditions.md)', '[Conditions](https://example.com/Conditions.md)'),
    ('Root anchor', '[Prone](#prone)', '[Prone](#prone)'),
    ('Existing page path', '[Conditions](/SkroxiousDM/house-rules/conditions/)', '[Conditions](' + ROUTE + ')'),
    ('Unresolved wiki', '[[Unknown page]]', '[[Unknown page]]'),
]

class HouseRuleLinkTests(unittest.TestCase):
    def test_regressions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'docs/7. House Rules'
            source.mkdir(parents=True)
            contents = {
                'Conditions.md': '# Conditions\n# Prone\n# Incapacitated\n',
                'Actions in Combat.md': '# Actions in Combat\n## Hide [Action]\n',
                'Nested/Group Checks.md': '# Group Checks\n',
            }
            routes, names = {}, {}
            for name, text in contents.items():
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding='utf-8')
                route = {'Conditions.md': '/house-rules/conditions/', 'Actions in Combat.md': '/house-rules/actions-in-combat/', 'Nested/Group Checks.md': '/house-rules/nested/group-checks/'}[name]
                routes[path.resolve()] = route
                names.setdefault(path.stem.casefold(), []).append(path.resolve())
            _, convert = make_converter(root, source, '/SkroxiousDM', routes, names)
            for label, text, expected in CASES:
                with self.subTest(case=label):
                    self.assertEqual(convert(text, source / 'Actions in Combat.md'), expected)
            rendered = convert(contents['Conditions.md'], source / 'Conditions.md')
            self.assertIn('<a id="hr-prone"></a>', rendered)
            self.assertIn('<a id="hr-incapacitated"></a>', rendered)

if __name__ == '__main__':
    unittest.main()
