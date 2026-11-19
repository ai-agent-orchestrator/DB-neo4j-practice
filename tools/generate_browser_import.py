"""Generate a self-contained, model-free graph import for other Neo4j users."""
import json
from pathlib import Path
from urllib.parse import urlencode, quote

ROOT = Path(__file__).resolve().parent.parent


def literal(value):
    if isinstance(value, dict):
        return '{' + ', '.join(key + ': ' + literal(item) for key, item in value.items()) + '}'
    if isinstance(value, list):
        return '[' + ',\n    '.join(literal(item) for item in value) + ']'
    return json.dumps(value, ensure_ascii=False)


def main():
    data = json.loads((ROOT / 'frontend/public/data/graph.json').read_text(encoding='utf-8'))
    groups = [
        ('traits', data['traits'], '''MERGE (t:SharedTrait:MbtiTrait {key: row.id})
    SET t.title=row.title, t.name=row.title'''),
        ('types', data['types'], '''MERGE (m:MbtiType {code: row.code}) SET m.name=row.code
    WITH row, m UNWIND row.traits AS key
    MATCH (t:SharedTrait {key:key}) MERGE (m)-[:HAS_TRAIT]->(t)'''),
        ('signs', data['signs'], '''MERGE (z:ZodiacSign {id:row.id}) SET z.name=row.name, z.is_demo=true
    WITH row, z UNWIND row.traits AS key
    MATCH (t:SharedTrait {key:key}) MERGE (z)-[:HAS_TRAIT]->(t)'''),
        ('chunks', [{key: card[key] for key in ['id','title','text','category','document_id','document_title','source','traits','tips']}
                    for card in data['chunks']], '''MERGE (d:RagDocument {id:row.document_id})
    SET d.title=row.document_title, d.name=row.document_title, d.source=row.source, d.is_demo=true
    MERGE (c:RagChunk {id:row.id})
    SET c.title=row.title, c.name=row.title, c.text=row.text, c.category=row.category
    MERGE (c)-[:FROM_DOCUMENT]->(d)
    WITH row, c UNWIND row.traits AS key
    MATCH (t:SharedTrait {key:key}) MERGE (t)-[:FROM_CHUNK]->(c)'''),
        ('suggestions', data['suggestions'], '''MERGE (i:RagTip {id:row.id}) SET i.text=row.text, i.name=row.text
    WITH row, i MATCH (t:SharedTrait {key:row.trait}) MERGE (t)-[:SUGGESTS]->(i)'''),
        ('evidence', [{'id':c['id'],'tips':c['tips']} for c in data['chunks']], '''MATCH (c:RagChunk {id:row.id})
    WITH row, c UNWIND row.tips AS key
    MATCH (i:RagTip {id:key}) MERGE (i)-[:FROM_CHUNK]->(c)'''),
    ]
    parts = ['// Fictional Lumi graph only. No password, model, embedding vectors, APOC or Python required.',
             '// Select your own learning database in Neo4j Browser, paste this ENTIRE file, then Run.',
             '// Does not delete data. Sequential re-runs reuse stable IDs; use a dedicated lab database.']
    for name, rows, query in groups:
        parts.append('CALL () {\n    UNWIND ' + literal(rows) + ' AS row\n    ' + query
                     + '\n    RETURN count(*) AS imported_' + name + '\n}')
    parts.append('RETURN ' + ', '.join('imported_' + name for name, _, _ in groups) + ';\n')
    (ROOT / 'cypher/lumi_graph_only_seed.cypher').write_text('\n'.join(parts), encoding='utf-8')
    graph_query = (ROOT / 'cypher/lumi_all_graph.cypher').read_text(encoding='utf-8')
    graph_query = '\n'.join(line for line in graph_query.splitlines() if not line.startswith('//'))
    link = 'http://localhost:7474/browser/?' + urlencode({'cmd':'edit','arg':graph_query}, quote_via=quote)
    (ROOT / 'docs/NEO4J_BROWSER_LINK.txt').write_text(link + '\n', encoding='utf-8')
    for relative in ['README.md','README.en.md','docs/OPEN_IN_NEO4J.md']:
        path = ROOT / relative
        if path.is_file():
            path.write_text(path.read_text(encoding='utf-8').replace('NEO4J_BROWSER_GRAPH_LINK',link),encoding='utf-8')
    print('Generated graph-only import and password-free Browser query link')


if __name__ == '__main__':
    main()
