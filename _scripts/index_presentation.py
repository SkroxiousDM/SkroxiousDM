"""Presentation-only grouping for generated documentation indexes."""
from collections import Counter, defaultdict
from pathlib import PurePosixPath
import re

GROUPS = {
    '1. Start Here': {
        'Getting Started': 'Player primer|Character Creation Primer|Character Creation Steps',
        'Abilities and Advancement': 'Ability Scores|XP per level',
        'Personality and Backstory': 'Backstory Questions|Beliefs|Bond|Code of Honor|Complication|Flaw|Motivation|Orphan Details|Passions-and-Insights',
    },
    '2. Origins': {
        'Origins and Backgrounds': 'Origin|Ancestries-and-Backgrounds',
        'Ancestries': 'Changeling|Dwarves|Goblins|Humans|Ogres',
    },
    '3.Classes': {
        'Class Overview': 'Class',
        'Classes': 'Captain|Hunter|Mystic|Scoundrel|Warrior',
        'Work in Progress': 'Beowulf-AoH-WIP',
    },
    '4.Feats': {
        'Character Creation': 'Character Creation Feat|Origin Feats|Burden',
        'Feats and Advancement': 'Class Feats|General Feats|Classless-Advancements',
    },
    '5.Equipment': {
        'Equipment Overview': 'equipment',
        'Arms and Armor': 'Armor|Weapons',
        'Tools and Special Items': 'Tools|Alchemical Elixirs|Lesser Artifacts',
    },
    '6.Spells': {
        'Spell Lists': 'Spell Lists',
        'Spell Descriptions': 'Spell Descriptions',
        'Additional Magic': 'extra spells|mythos-spells',
        'Work in Progress': 'WIP-spells',
    },
    '7. House Rules': {
        'Combat and Tactics': 'Actions in Combat|Called Shots|Crueler Critical Hits|Exhausting_Combat|Expanded Actions|Group Checks|Initiative|Mounted Combat|Party_Retreat|battleforms|cover-elevation-flanking|fighting-masteries|fighting-styles|martial-maneuvers|weapon-mastery',
        'Checks and Social Play': 'GumshoeMechanics|Ingenious Proficiency|Metagaming_and_Tabletalk|New modifiers for persuasion tests|Pushing_a_Roll|Secret_DCs|Skill Proficiency|Social Challenges|Success_and_Failure',
        'Health, Rest and Recovery': 'Conditions|Fate Points|Resting_and_Healing|Resurrection|Wounds_and_Hit-Protection',
        'Magic, Corruption and Horror': 'Corruption_and_Shadow|Horror_and_Madness|OVEREXTENDING_and_MISCASTING|Scarier_Undead',
        'Exploration and Environment': 'Darkvision|Falling|Underwater_Combat',
        'Advancement and Economy': 'Silver_Standard_Economy|Training_to_Level_Up',
    },
    'RoS-CoS-RRL': {
        'Characters and Party': 'Player characters',
        'Journals and Recaps': 'Recap',
    },
    'simple-quest': {'Quests': 'quests', 'Lore': 'lore'},
}


def clean_title(value):
    value = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', value)
    value = re.sub(r'[_-]+', ' ', value)
    value = re.sub(r'^\s*\d+[. )_-]*\s*', '', value)
    value = ' '.join(value.split())
    if value.islower() or value.isupper():
        value = value.title()
    return value or 'Untitled'


def category_for(section, relative):
    path = PurePosixPath(relative)
    parts = path.parts[1:] if path.parts and path.parts[0] == section else path.parts
    candidates = {path.stem.casefold()}
    candidates.update(part.casefold() for part in parts[:-1])
    for category, values in GROUPS.get(section, {}).items():
        if candidates.intersection(value.casefold() for value in values.split('|')):
            return category
    if len(parts) > 1:
        return clean_title(parts[0])
    return 'Other Documents'


def escape_label(value):
    return value.replace('\\', '\\\\').replace('[', r'\[').replace(']', r'\]')


def render_index(section, entries, base='', heading_level=2):
    """Render each input route once; do not change routing or publication policy."""
    grouped = defaultdict(list)
    for relative, route in entries:
        path = PurePosixPath(relative)
        grouped[category_for(section, relative)].append((clean_title(path.stem), path, route))
    order = list(GROUPS.get(section, {}))
    categories = sorted(grouped, key=lambda name: (order.index(name) if name in order else len(order), name.casefold()))
    result = []
    for category in categories:
        result.extend(['#' * heading_level + ' ' + category, ''])
        items = sorted(grouped[category], key=lambda item: (item[0].casefold(), item[1].as_posix().casefold()))
        counts = Counter(title.casefold() for title, _, _ in items)
        for title, path, route in items:
            if counts[title.casefold()] > 1:
                title += ' — ' + clean_title(path.parent.name)
            result.append('- [' + escape_label(title) + '](' + base + route + ')')
        result.append('')
    return '\n'.join(result)
