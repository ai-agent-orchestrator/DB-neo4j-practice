import unittest
from mbti_lab.data import TYPES, result


class DataTests(unittest.TestCase):
    def test_all_types_have_closed_graphs(self):
        self.assertEqual(len(set(TYPES)), 16)
        for code in TYPES:
            payload = result(code)
            ids = {n['id'] for n in payload['nodes']}
            self.assertEqual(len(ids), 9)
            self.assertEqual(len(payload['edges']), 8)
            self.assertEqual(len(payload['traits']), 4)
            for edge in payload['edges']:
                self.assertIn(edge['source'], ids)
                self.assertIn(edge['target'], ids)

    def test_invalid_type_rejected(self):
        with self.assertRaises(ValueError):
            result('INVALID')
