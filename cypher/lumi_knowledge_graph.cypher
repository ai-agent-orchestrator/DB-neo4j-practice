// Neo4j Browser: select mbti-zodiac first (:use mbti-zodiac).
// Run this query and select Graph view.
MATCH p = (m:MbtiType {code:'INTJ'})-[:HAS_TRAIT]->(t:SharedTrait)
          <-[:HAS_TRAIT]-(z:ZodiacSign {name:'물병자리'})
OPTIONAL MATCH q = (t)-[:FROM_CHUNK]->(c:RagChunk)
                   -[:FROM_DOCUMENT]->(:RagDocument)
OPTIONAL MATCH r = (t)-[:SUGGESTS]->(tip:RagTip)-[:FROM_CHUNK]->(c)
RETURN p, q, r
LIMIT 40;
