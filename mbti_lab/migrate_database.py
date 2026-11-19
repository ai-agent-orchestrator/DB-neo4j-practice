"""Move the lab graph to mbti-zodiac, preserving a local JSON backup.

Stop lab writers first. Requires database creation permission (multi-DB Neo4j).
Run from the repository root: python -m mbti_lab.migrate_database
"""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from dotenv import dotenv_values, set_key
from neo4j import GraphDatabase

from .database import DATABASE

ROOT = Path(__file__).resolve().parent.parent
SOURCE = 'ohgirestaurant-graph'
LABELS = ['MbtiType', 'MbtiTrait', 'MbtiInsight', 'MbtiSource',
          'SharedTrait', 'ZodiacSign', 'AstrologySource']


def snapshot(tx):
    nodes = [r.data() for r in tx.run('''
        MATCH (n) WHERE any(l IN labels(n) WHERE l IN $labels)
        RETURN elementId(n) AS id, labels(n) AS labels, properties(n) AS props
        ''', labels=LABELS)]
    ids = [n['id'] for n in nodes]
    edges = [r.data() for r in tx.run('''
        MATCH (a)-[r]->(b) WHERE elementId(a) IN $ids OR elementId(b) IN $ids
        RETURN elementId(a) AS start, elementId(b) AS end,
               type(r) AS type, properties(r) AS props
        ''', ids=ids)]
    if any(e['start'] not in ids or e['end'] not in ids for e in edges):
        raise RuntimeError('External relationships found; refusing to move shared nodes.')
    return {'nodes': nodes, 'edges': edges}


def signature(graph):
    def canonical(value):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    nodes = {n['id']: canonical([sorted(n['labels']), n['props']])
             for n in graph['nodes']}
    return (Counter(nodes.values()), Counter(
        canonical([nodes[e['start']], e['type'], e['props'], nodes[e['end']]])
        for e in graph['edges']))


def quoted(value):
    return '`' + value.replace('`', '``') + '`'


def main():
    env_path = ROOT / '.env.mbti'
    config = dotenv_values(env_path)
    with GraphDatabase.driver(config['NEO4J_URI'], auth=(
        config.get('NEO4J_USERNAME', 'neo4j'), config['NEO4J_PASSWORD']),
        max_transaction_retry_time=0) as driver:
        with driver.session(database=SOURCE) as session:
            graph = session.execute_read(snapshot)
            before = session.run('MATCH (n) RETURN count(n) AS n').single()['n']
        if not graph['nodes']:
            raise RuntimeError('No source lab nodes; nothing changed.')
        backup = ROOT / 'backups' / ('mbti-zodiac-' +
            datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
        backup.parent.mkdir(exist_ok=True)
        backup.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding='utf-8')
        driver.execute_query('CREATE DATABASE `mbti-zodiac` IF NOT EXISTS WAIT', database_='system')

        def copy(tx):
            if tx.run('MATCH (n) RETURN count(n) AS n').single()['n']:
                raise RuntimeError('Target must be empty; source and backup retained.')
            mapping = {}
            for node in graph['nodes']:
                labels = ':'.join(quoted(l) for l in node['labels'])
                mapping[node['id']] = tx.run(
                    f'CREATE (n:{labels}) SET n = $props RETURN elementId(n) AS id',
                    props=node['props']).single()['id']
            for edge in graph['edges']:
                tx.run('MATCH (a), (b) WHERE elementId(a)=$a AND elementId(b)=$b '
                       f'CREATE (a)-[r:{quoted(edge["type"])}]->(b) SET r=$props',
                       a=mapping[edge['start']], b=mapping[edge['end']],
                       props=edge['props']).consume()
            if signature(snapshot(tx)) != signature(graph):
                raise RuntimeError('Target verification failed; rolling back.')

        with driver.session(database=DATABASE) as session:
            session.execute_write(copy)

        def cleanup(tx):
            current = snapshot(tx)
            if (signature(current) != signature(graph) or
                    {n['id'] for n in current['nodes']} != {n['id'] for n in graph['nodes']}):
                raise RuntimeError('Source changed; source retained. Stop writers and review backup.')
            tx.run('MATCH (n) WHERE elementId(n) IN $ids DETACH DELETE n',
                   ids=[n['id'] for n in graph['nodes']]).consume()
            remaining = tx.run('MATCH (n) RETURN count(n) AS n').single()['n']
            if remaining != before - len(graph['nodes']):
                raise RuntimeError('Unexpected remaining node count; rolling back cleanup.')
            return remaining

        with driver.session(database=SOURCE) as session:
            remaining = session.execute_write(cleanup)
        set_key(str(env_path), 'NEO4J_DATABASE', DATABASE, quote_mode='never')
        print(f'PASS: {len(graph["nodes"])} nodes, {len(graph["edges"])} relationships moved to {DATABASE}')
        print(f'{SOURCE}: {remaining} other nodes retained. Backup: {backup}')


if __name__ == '__main__':
    main()
