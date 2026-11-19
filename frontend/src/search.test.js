import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {cosine,vectorSearch,expandGraph,makePrompt} from './search.js';
const data=JSON.parse(readFileSync(new URL('../public/data/graph.json',import.meta.url),'utf8'));
test('vector invariants reject mismatched and zero vectors',()=>{
  assert.equal(cosine([1,0],[1,0]),1);assert.equal(cosine([1,0],[0,1]),0);
  assert.throws(()=>cosine([1],[1,2]));assert.throws(()=>cosine([0],[1]));
});
test('Korean travel probe finds a relevant card',()=>{
  const seeds=vectorSearch(data,data.probe.embedding);
  assert.equal(seeds.length,3);assert.equal(seeds[0].id,'scenario-25');
});
test('graph extensions are supported by explicit paths and exclude seed chunks',()=>{
  const seeds=vectorSearch(data,data.probe.embedding);
  const seedIds=seeds.map(c=>c.id);
  for(const type of data.types)for(const sign of data.signs){
    const paths=expandGraph(data,seeds,type.code,sign.id);
    assert.ok(paths.length>0&&paths.length<=5);
    for(const path of paths){
      assert.ok(!seedIds.includes(path.chunk.id));
      assert.ok(path.chunk.traits.includes(path.trait));
      assert.ok(path.chunk.tips.includes(path.tip.id));
      assert.equal(path.tip.trait,path.trait);
      assert.ok(path.via.every(id=>seeds.find(s=>s.id===id).traits.includes(path.trait)));
    }
  }
});
test('prompt includes traceable evidence and question without network calls',()=>{
  const seeds=vectorSearch(data,data.probe.embedding);
  const paths=expandGraph(data,seeds,'INTJ','aquarius');
  const prompt=makePrompt('旅行？','INTJ','물병자리',seeds,paths);
  assert.ok(prompt.includes('旅行？'));assert.ok(prompt.includes('scenario-25'));
});
