"""Repeatable synthetic provenance experiment; no LLM/API key required."""
import argparse
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['seed', 'query'])
    parser.add_argument('--keyword', default='배달비')
    args = parser.parse_args()

    from dotenv import load_dotenv
    from neo4j import GraphDatabase

    load_dotenv(ROOT / '.env.delivery')
    required = ['NEO4J_URI', 'NEO4J_PASSWORD', 'NEO4J_DATABASE']
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        parser.error('Set these in .env.delivery: ' + ', '.join(missing))
    database = os.environ['NEO4J_DATABASE']
    filename = 'delivery_seed.cypher' if args.action == 'seed' else 'delivery_paths.cypher'
    cypher = (ROOT / 'cypher' / filename).read_text(encoding='utf-8')
    try:
        with GraphDatabase.driver(
            os.environ['NEO4J_URI'],
            auth=(os.getenv('NEO4J_USERNAME', 'neo4j'), os.environ['NEO4J_PASSWORD']),
        ) as driver:
            driver.verify_connectivity()
            print(f'Database: {database}')
            # A single transaction for all seed writes; reads use read routing.
            with driver.session(database=database) as session:
                def execute(tx):
                    return [record.data() for record in tx.run(cypher, keyword=args.keyword)]
                rows = (session.execute_write(execute) if args.action == 'seed'
                        else session.execute_read(execute))
            for row in rows:
                row.pop('p', None)
                print(row)
            if not rows:
                print('No matching paths. Run seed first or check the keyword/database.')
    except Exception as exc:
        # Do not print credentials or a potentially credential-bearing URI.
        parser.exit(1, f'Neo4j operation failed ({type(exc).__name__}). '
                    'Check the server, credentials, database, and Cypher files.\n')


if __name__ == '__main__':
    main()
