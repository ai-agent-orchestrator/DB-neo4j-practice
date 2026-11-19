import unittest

from mbti_lab.database import project_database


class DatabaseIsolationTest(unittest.TestCase):
    def test_accepts_project_database(self):
        self.assertEqual(project_database('mbti-zodiac'), 'mbti-zodiac')

    def test_rejects_restaurant_or_default_database(self):
        for name in ('ohgirestaurant-graph', 'neo4j', '', None):
            with self.subTest(name=name), self.assertRaises(ValueError):
                project_database(name)
