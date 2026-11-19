"""Seed a fictional 12-sign/MBTI crossover for graph learning; no predictions."""
import os
from pathlib import Path
from .database import project_database

# Deliberately authored toy mappings, not empirical personality claims.
SIGNS = [
    ('aries', '양자리', 'EP'), ('taurus', '황소자리', 'SJ'),
    ('gemini', '쌍둥이자리', 'EN'), ('cancer', '게자리', 'IF'),
    ('leo', '사자자리', 'EF'), ('virgo', '처녀자리', 'TJ'),
    ('libra', '천칭자리', 'FP'), ('scorpio', '전갈자리', 'IT'),
    ('sagittarius', '사수자리', 'NP'), ('capricorn', '염소자리', 'SJ'),
    ('aquarius', '물병자리', 'NT'), ('pisces', '물고기자리', 'NF'),
]

SEED = '''
UNWIND $rows AS row
MERGE (z:ZodiacSign {id: row.id})
SET z.name = row.name, z.is_demo = true
MERGE (t:MbtiTrait {key: row.key})
SET t.title = row.title, t.text = row.text
SET t:SharedTrait
MERGE (z)-[:HAS_TRAIT]->(t)
MERGE (s:AstrologySource {id: 'astrology-toy-v1'})
SET s.title = '12별자리 연결 실습용 직접 작성한 가상 매핑', s.is_demo = true
MERGE (z)-[:FROM_SOURCE]->(s)
RETURN count(*) AS processed
'''


def main():
    from dotenv import load_dotenv
    from neo4j import GraphDatabase
    from .data import TRAITS, TYPES
    from .server import SEED as MBTI_SEED

    load_dotenv(Path(__file__).resolve().parent.parent / '.env.mbti')
    required = ['NEO4J_URI', 'NEO4J_PASSWORD', 'NEO4J_DATABASE']
    if any(not os.getenv(key) for key in required):
        raise SystemExit('Complete .env.mbti first.')
    database = project_database(os.environ['NEO4J_DATABASE'])
    mbti_rows = [{'code': code, 'key': key, 'title': TRAITS[key][0],
                  'text': TRAITS[key][1], 'tip': TRAITS[key][2]}
                 for code in TYPES for key in code]
    rows = [{'id': sign, 'name': name, 'key': key,
             'title': TRAITS[key][0], 'text': TRAITS[key][1]}
            for sign, name, keys in SIGNS for key in keys]
    with GraphDatabase.driver(os.environ['NEO4J_URI'], auth=(
        os.getenv('NEO4J_USERNAME', 'neo4j'), os.environ['NEO4J_PASSWORD'])) as driver:
        def seed(tx):
            tx.run(MBTI_SEED, rows=mbti_rows).consume()
            tx.run(SEED, rows=rows).consume()
        with driver.session(database=database) as session:
            session.execute_write(seed)
        records, _, _ = driver.execute_query('''
            MATCH (z:ZodiacSign)-[:HAS_TRAIT]->(t:SharedTrait)
            WHERE z.id IN $ids
            RETURN count(DISTINCT z) AS signs, count(*) AS links,
                   count(DISTINCT t) AS shared_traits
            ''', ids=[s[0] for s in SIGNS], database_=database)
        counts = records[0].data()
        assert counts == {'signs': 12, 'links': 24, 'shared_traits': 8}, counts
        print(f'PASS {database}: {counts}')
        # Sequential re-runs should retain exactly these relationships.
        records, _, _ = driver.execute_query('''
            MATCH (m:MbtiType {code:'INTJ'})-[:HAS_TRAIT]->(t:SharedTrait)
                  <-[:HAS_TRAIT]-(z:ZodiacSign)
            RETURN z.name AS sign, collect(t.title) AS common_traits
            ORDER BY sign
            ''', database_=database)
        for record in records:
            print(record.data())


if __name__ == '__main__':
    main()
