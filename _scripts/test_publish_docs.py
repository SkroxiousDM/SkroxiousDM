from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from publish_docs import excluded, route_for, plan, page

class PublishingTests(unittest.TestCase):
    def test_archive_exclusion_is_recursive(self):
        self.assertTrue(excluded(Path('Curse-of-Strahd-Reloaded-main/act/note.md')))
        self.assertFalse(excluded(Path('1. Start Here/primer.md')))

    def test_deferred_manuscript(self):
        self.assertTrue(excluded(Path('nested/Arc_S-A_Sword_of_Sunlight.md')))

    def test_house_rule_urls_are_preserved(self):
        self.assertEqual(route_for(Path('7. House Rules/Conditions.md')), '/house-rules/conditions/')
        self.assertEqual(route_for(Path('7. House Rules/Sub Folder/Test Rule.md')), '/house-rules/sub-folder/test-rule/')

    def test_section_routes(self):
        self.assertEqual(route_for(Path('3.Classes/Class.md')), '/reference/classes/class/')
        self.assertEqual(route_for(Path('simple-quest/lore/lore-contents.md')), '/campaign/quests-and-lore/lore/lore-contents/')
        self.assertEqual(route_for(Path('index.md')), '/reference/overview/')

    def test_recursive_plan(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('1. Start Here/sub/Primer.markdown', '7. House Rules/Conditions.md', 'Curse-of-Strahd-Reloaded-main/hidden.md', 'Arc_S-A_Sword_of_Sunlight.md', 'image.png'):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('# Test', encoding='utf-8')
            routes, names = plan(root)
            self.assertEqual(len(routes), 2)
            self.assertIn('conditions', names)

    def test_duplicate_routes_fail(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'A B.md').write_text('a')
            (root / 'A-B.md').write_text('b')
            with self.assertRaises(ValueError):
                plan(root)

    def test_safe_front_matter(self):
        self.assertIn('title: "A: B"', page('A: B', '/reference/test/', 'Body'))

if __name__ == '__main__':
    unittest.main()
