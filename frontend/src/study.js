export function evidenceCypher(path){
 const seed=path.via[0];
 if(!/^scenario-\d+$/.test(seed)||!/^scenario-\d+$/.test(path.chunk.id)||!/^[A-Z]$/.test(path.trait)||!/^[a-z]+$/.test(path.tip.id))throw Error('Invalid graph identifier');
 return `// Neo4j Browser: :use mbti-zodiac\nMATCH p = (seed:RagChunk {id:'${seed}'})<-[:FROM_CHUNK]-(t:SharedTrait {key:'${path.trait}'})\n          -[:FROM_CHUNK]->(other:RagChunk {id:'${path.chunk.id}'})\n          <-[:FROM_CHUNK]-(tip:RagTip {id:'${path.tip.id}'})\nMATCH (t)-[:SUGGESTS]->(tip)\nMATCH q = (other)-[:FROM_DOCUMENT]->(:RagDocument)\nRETURN p, q;`;
}
