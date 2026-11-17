import unittest
from index_presentation import GROUPS, clean_title, category_for, render_index

class IndexPresentationTests(unittest.TestCase):
    def test_all_sections_have_categories(self):
        self.assertEqual(len(GROUPS), 9)

    def test_clean_titles(self):
        self.assertEqual(clean_title('Corruption_and_Shadow'), 'Corruption and Shadow')
        self.assertEqual(clean_title('0 Spell Lists'), 'Spell Lists')
        self.assertEqual(clean_title('GumshoeMechanics'), 'Gumshoe Mechanics')
        self.assertEqual(clean_title('XP per level'), 'XP per level')

    def test_house_rules(self):
        self.assertEqual(category_for('7. House Rules', '7. House Rules/Actions in Combat.md'), 'Combat and Tactics')

    def test_nested_spells(self):
        self.assertEqual(category_for('6.Spells', '6.Spells/Spell Descriptions/Level 1/Fire.md'), 'Spell Descriptions')

    def test_campaign_categories(self):
        self.assertEqual(category_for('RoS-CoS-RRL', 'RoS-CoS-RRL/Recap/Journal.md'), 'Journals and Recaps')
        self.assertEqual(category_for('simple-quest', 'simple-quest/quests/quests.md'), 'Quests')

    def test_unknown_documents_retained(self):
        text = render_index('7. House Rules', [('7. House Rules/New Rule.md', '/house-rules/new-rule/')])
        self.assertIn('## Other Documents', text)
        self.assertIn('[New Rule](/house-rules/new-rule/)', text)

    def test_sorting_base_and_routes(self):
        entries = [('5.Equipment/Weapons.md', '/reference/equipment/weapons/'), ('5.Equipment/Armor.md', '/reference/equipment/armor/')]
        text = render_index('5.Equipment', entries, '/SkroxiousDM')
        self.assertLess(text.index('[Armor]'), text.index('[Weapons]'))
        for _, route in entries:
            self.assertEqual(text.count('(/SkroxiousDM' + route + ')'), 1)
        self.assertNotIn('.md', text)
        self.assertEqual(text, render_index('5.Equipment', list(reversed(entries)), '/SkroxiousDM'))

    def test_duplicates_get_context(self):
        text = render_index('', [('one/Note.md', '/one/'), ('two/Note.md', '/two/')])
        self.assertIn('(/one/)', text)
        self.assertIn('(/two/)', text)

    def test_markdown_escaping(self):
        text = render_index('', [('A [B].md', '/test/')])
        self.assertIn(r'A \[B\]', text)

    def test_main_library_subheadings(self):
        text = render_index('5.Equipment', [('5.Equipment/Armor.md', '/armor/')], heading_level=3)
        self.assertTrue(text.startswith('### Arms and Armor'))
