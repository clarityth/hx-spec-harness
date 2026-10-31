import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('skill_search', Path(__file__).resolve().parents[1] / 'tools/find_external_skills.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SkillLibraryTests(unittest.TestCase):
    def test_restricted_and_duplicate_sources_are_not_default_choices(self):
        rows = [
            {'name': 'architecture-designer', 'description': 'system design', 'mode': 'conditional', 'path': 'a'},
            {'name': 'architecture-browser', 'description': 'system design', 'mode': 'reference-only', 'path': 'b'},
            {'name': 'architecture-designer', 'description': 'system design', 'mode': 'conditional', 'path': 'c', 'alias_of': 'a'},
        ]
        self.assertEqual([r['path'] for r in module.search(rows, '아키텍처')], ['a'])
        self.assertEqual({r['path'] for r in module.search(rows, '아키텍처', True)}, {'a', 'b'})

    def test_no_matches_are_not_invented(self):
        self.assertEqual(module.search([{'name': 'tdd', 'description': 'tests', 'mode': 'conditional', 'path': 'a'}], 'unknown-topic'), [])
