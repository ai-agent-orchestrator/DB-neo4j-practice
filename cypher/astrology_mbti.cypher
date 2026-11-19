// Change INTJ and/or 물병자리 to explore other combinations.
MATCH p = (m:MbtiType {code: 'INTJ'})-[:HAS_TRAIT]->(t:SharedTrait)
          <-[:HAS_TRAIT]-(z:ZodiacSign {name: '물병자리'})
RETURN p;
