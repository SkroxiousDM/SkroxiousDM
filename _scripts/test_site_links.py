import tempfile
import unittest
from pathlib import Path
from site_links import make_converter, read_site_config

class SiteLinkTests(unittest.TestCase):
    def test_both_site_configurations(self):
        for base, url in [('', 'https://skroxiousdm.com'), ('/SkroxiousDM', 'https://skroxiousdm.github.io')]:
            with self.subTest(base=base), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source = root / 'docs/7. House Rules'
                source.mkdir(parents=True)
                conditions = source / 'Conditions.md'
                current = source / 'Actions in Combat.md'
                conditions.write_text('# Conditions\n# Prone\n', encoding='utf-8')
                current.write_text('# Actions in Combat\n', encoding='utf-8')
                routes = {conditions.resolve(): '/house-rules/conditions/', current.resolve(): '/house-rules/actions-in-combat/'}
                names = {'conditions': [conditions.resolve()], 'actions in combat': [current.resolve()]}
                resolve, convert = make_converter(root, source, base, routes, names, site_url=url)
                expected = base + '/house-rules/conditions/?mode=full#prone'
                for target in ['Conditions.md?mode=full#prone', 'https://skroxiousdm.github.io/SkroxiousDM/7.%20House%20Rules/Conditions?mode=full#prone', '/SkroxiousDM/house-rules/conditions/?mode=full#prone']:
                    self.assertEqual(resolve(target, current), expected)
                self.assertEqual(convert('[Prone]', current), '[Prone](' + base + '/house-rules/conditions/#hr-prone)')
                self.assertEqual(convert('[conditions]: Conditions.md "Rules"', current), '[conditions]: ' + base + '/house-rules/conditions/ "Rules"')
                self.assertEqual(convert('[Conditions](<Conditions.md> "Rules")', current), '[Conditions](<' + base + '/house-rules/conditions/> "Rules")')
                code = '`[Conditions](Conditions.md)`'
                self.assertEqual(convert(code, current), code)
                external = 'https://skroxiousdm.github.io/Other/Conditions'
                self.assertEqual(resolve(external, current), external)
                config = root / '_config.yml'
                config.write_text('url: "' + url + '"\nbaseurl: "' + base + '"\n', encoding='utf-8')
                self.assertEqual(read_site_config(config), (url, base))
                if not base:
                    custom = 'https://skroxiousdm.com/7.%20House%20Rules/Conditions?mode=full#prone'
                    self.assertEqual(resolve(custom, current), expected)

if __name__ == '__main__':
    unittest.main()
