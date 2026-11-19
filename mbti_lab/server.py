"""Local MBTI graph lab: python -m mbti_lab.server [--seed] [--demo]."""
import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .data import TYPES, TRAITS, result
from .database import project_database

ROOT = Path(__file__).resolve().parent
SEED = '''
UNWIND $rows AS row
MERGE (m:MbtiType {code: row.code})
MERGE (t:MbtiTrait {key: row.key})
SET t.title = row.title, t.text = row.text
MERGE (i:MbtiInsight {key: row.key}) SET i.text = row.tip
MERGE (s:MbtiSource {id: 'mbti-lab-original-v1'})
SET s.title = 'MBTI Graph Lab 직접 작성한 재미용 예시', s.is_demo = true
MERGE (m)-[:HAS_TRAIT]->(t)
MERGE (t)-[:SUGGESTS]->(i)
MERGE (i)-[:FROM_SOURCE]->(s)
RETURN count(*) AS processed
'''
QUERY = '''
MATCH (m:MbtiType {code: $code})-[:HAS_TRAIT]->(t:MbtiTrait)
MATCH (t)-[:SUGGESTS]->(i:MbtiInsight)-[:FROM_SOURCE]->(s:MbtiSource {id: 'mbti-lab-original-v1'})
RETURN t.key AS id, t.title AS title, t.text AS text, i.text AS tip, s.title AS source
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', action='store_true')
    parser.add_argument('--demo', action='store_true', help='Use example data without Neo4j')
    parser.add_argument('--port', type=int, default=8016)
    args = parser.parse_args()
    driver = None
    database = None
    if args.demo and args.seed:
        parser.error('--seed requires Neo4j mode')
    if not args.demo:
        from dotenv import load_dotenv
        from neo4j import GraphDatabase
        load_dotenv(ROOT.parent / '.env.mbti')
        required = ['NEO4J_URI', 'NEO4J_PASSWORD', 'NEO4J_DATABASE']
        if any(not os.getenv(key) for key in required):
            parser.error('Complete .env.mbti first, or use --demo for a UI preview.')
        database = project_database(os.environ['NEO4J_DATABASE'])
        driver = GraphDatabase.driver(os.environ['NEO4J_URI'], auth=(
            os.getenv('NEO4J_USERNAME', 'neo4j'), os.environ['NEO4J_PASSWORD']))
        driver.verify_connectivity()
        if args.seed:
            rows = [{'code': code, 'key': key, 'title': TRAITS[key][0],
                     'text': TRAITS[key][1], 'tip': TRAITS[key][2]}
                    for code in TYPES for key in code]
            driver.execute_query(SEED, rows=rows, database_=database)
            print(f'Seeded 16 types into {database}', flush=True)

    class Handler(BaseHTTPRequestHandler):
        def send_json(self, payload, status=200):
            data = json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == '/api/health':
                self.send_json({'mode': 'demo' if args.demo else 'neo4j'})
            elif path.startswith('/api/result/'):
                code = path.rsplit('/', 1)[-1].upper()
                if code not in TYPES:
                    self.send_json({'error': '올바른 유형을 선택해주세요.'}, 400)
                    return
                payload = result(code)
                if driver:
                    try:
                        records, _, _ = driver.execute_query(QUERY, code=code, database_=database,
                                                             routing_='r')
                        traits = {r['id']: r.data() for r in records}
                        if set(traits) != set(code):
                            self.send_json({'error': '실습 데이터가 없습니다. --seed로 실행해주세요.'}, 409)
                            return
                        payload['traits'] = [traits[key] for key in code]
                        for node in payload['nodes']:
                            if node['kind'] == 'trait':
                                node['label'] = traits[node['id']]['title']
                            elif node['kind'] == 'tip':
                                node['label'] = traits[node['id'][4:]]['tip']
                    except Exception:
                        self.send_json({'error': 'Neo4j 조회에 실패했습니다. 서버 연결을 확인해주세요.'}, 503)
                        return
                payload['mode'] = 'demo' if args.demo else 'neo4j'
                self.send_json(payload)
            elif path in ('/', '/index.html'):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write((ROOT / 'index.html').read_bytes())
            else:
                self.send_json({'error': 'Not found'}, 404)

    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'http://127.0.0.1:{args.port} — {"DEMO" if args.demo else "NEO4J"}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        if driver:
            driver.close()


if __name__ == '__main__':
    main()
