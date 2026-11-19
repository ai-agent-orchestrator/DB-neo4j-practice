MATCH p = (e:__Entity__)-[:FROM_CHUNK]->(c:Chunk)-[:FROM_DOCUMENT]->(d:Document)
WHERE e.name CONTAINS $keyword
  AND d.id IN ['demo-delivery-doc-001', 'demo-delivery-doc-002']
RETURN e.name AS entity, c.text AS chunk, d.id AS document_id, d.title AS title, p;
