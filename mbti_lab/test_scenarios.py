import unittest
from mbti_lab.scenarios import cards, SUGGESTIONS
from mbti_lab.data import TRAITS


class ScenarioTests(unittest.TestCase):
    def test_each_suggestion_has_explicit_evidence(self):
        rows = cards()
        self.assertEqual(len(rows), 60)
        self.assertEqual(len({r['id'] for r in rows}), 60)
        self.assertEqual(len(SUGGESTIONS), 24)
        by_id = {key: trait for key, trait, _ in SUGGESTIONS}
        for row in rows:
            self.assertTrue(set(row['traits']) <= set(TRAITS))
            self.assertEqual(set(row['traits']), {by_id[key] for key in row['tips']})
        self.assertEqual({key for row in rows for key in row['tips']}, set(by_id))
