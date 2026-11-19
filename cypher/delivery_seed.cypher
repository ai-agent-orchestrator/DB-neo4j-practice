// Synthetic learning data, not legal or restaurant policy.
UNWIND [
  {id: 'demo-delivery-doc-001', chunk: 'demo-delivery-chunk-001', title: '배달 주문 안내 — 실습 예시', text: '배달비는 주문 금액과 배달 거리에 따라 달라집니다.'},
  {id: 'demo-delivery-doc-002', chunk: 'demo-delivery-chunk-002', title: '주문 취소 안내 — 실습 예시', text: '주문 취소 시 배달비 환불 여부는 배달 진행 상태에 따라 달라집니다.'}
] AS row
MERGE (d:Document {id: row.id})
SET d.title = row.title, d.text = row.text, d.is_demo = true
MERGE (c:Chunk {id: row.chunk})
SET c.text = row.text, c.is_demo = true
MERGE (e:__Entity__ {name: '배달비'})
MERGE (e)-[:FROM_CHUNK]->(c)
MERGE (c)-[:FROM_DOCUMENT]->(d)
RETURN count(*) AS processed_documents;
