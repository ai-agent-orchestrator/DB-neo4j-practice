**Serverless · Google LiteRT-LM · On-device Search · Playground**

**Light. Free. Fun.**

# Explore Your Little Universe

### A fresh perspective on today's little dilemmas.

[한국어](README.md) | **English**

## [Open the playground — no installation](https://ai-agent-orchestrator.github.io/explore-your-little-universe/)

Meet Lumi, try a daily dilemma, and inspect the knowledge graph and source evidence. Use a current Chrome/Edge browser with WebGPU; the first actual search downloads an embedding model.

**[Open the full graph query in your own Neo4j Browser](http://localhost:7474/browser/?cmd=edit&arg=MATCH%20p%20%3D%20%28a%29-%5Br%5D-%3E%28b%29%0AWHERE%20type%28r%29%20IN%20%5B%27HAS_TRAIT%27%2C%27FROM_CHUNK%27%2C%27FROM_DOCUMENT%27%2C%27SUGGESTS%27%5D%0A%20%20AND%20any%28label%20IN%20labels%28a%29%20WHERE%20label%20IN%20%5B%27MbtiType%27%2C%27ZodiacSign%27%2C%27SharedTrait%27%2C%27RagChunk%27%2C%27RagTip%27%5D%29%0A%20%20AND%20any%28label%20IN%20labels%28b%29%20WHERE%20label%20IN%20%5B%27SharedTrait%27%2C%27RagChunk%27%2C%27RagTip%27%2C%27RagDocument%27%5D%29%0ARETURN%20p%0ALIMIT%20500%3B)** · **[First-time setup and graph import](docs/OPEN_IN_NEO4J.md)**

Start your local Neo4j instance and import the public example graph once. The link opens your own localhost and contains no password or another person's database connection.

![Lumi — A little insight. One small action.](docs/images/lumi.svg)

**An MBTI & Astrology Daily Action Playground**


Meet **Lumi**, a little star companion. Explore everyday dilemmas, discover connected perspectives, and try one small action. MBTI and astrology are playful fictional settings here, not validated predictions or clinical assessments.

## Static React + browser LiteRT-LM search

The React edition is included in `main`. Changes to `frontend` on `main` are tested, built, and deployed automatically by GitHub Actions.

No Spring server, Python web server, Ollama, database credentials, or paid API is required to run the page. Neo4j is used to build and inspect the graph. The published page reads an exported public snapshot and performs embedding, cosine search, and graph traversal on the visitor's device.

```text
Authoring: original scenario texts → LiteRT-LM embeddings → Neo4j → public snapshot
Browsing: React → on-device question embedding → vector search → graph expansion
```

### Run locally

Use Node.js 22.12+ and a recent Chrome or Edge browser with WebGPU enabled.

```powershell
git fetch origin
git switch main
cd frontend
npm ci
npm run dev
```

Open the printed address, normally http://127.0.0.1:5173. An explicitly marked example appears immediately. The first real search downloads a pinned public model (~165MB), verifies its SHA-256, and runs it locally. Model caching depends on browser storage availability; startup depends on device memory and WebGPU support.

### Explore

- **60 original scenario cards:** appointments, messages, work, rest, travel, choices, personal pace, family and relationships, creativity, and boundaries.
- **24 small action suggestions**, each linked to supporting source cards.
- **16 MBTI Lumi outfits** and **12 zodiac Lumi palettes and symbols**.
- **Vector only:** the three most similar scenario texts.
- **Vector + graph:** additional evidence and suggestions reached from those same texts.
- **Evidence view:** source IDs, original text, graph paths, and a Cypher query to inspect the corresponding nodes in Neo4j.
- **Gemini prompt:** copy a source-grounded prompt yourself. Nothing is automatically sent to Gemini.

The browser does not contact Neo4j at runtime. Changes in the authoring DB require re-exporting the snapshot and rebuilding the page. Questions are neither sent to an application server nor stored. Model downloads contact the public model host.

### Build for static hosting

```powershell
cd frontend
npm ci
npm test
npm run build
```

Publish `frontend/dist` on a static host. Relative paths support GitHub Pages project URLs. No `.env` file should be included. Hosting and bandwidth free tiers depend on the provider.

[Full setup, architecture and weekend checks](https://github.com/ai-agent-orchestrator/explore-your-little-universe/blob/feat/serverless-react-litert-rag/docs/STATIC_REACT_RAG.md) · [Scenario corpus](https://github.com/ai-agent-orchestrator/explore-your-little-universe/blob/feat/serverless-react-litert-rag/mbti_lab/scenarios.py) · [Neo4j seed/export code](https://github.com/ai-agent-orchestrator/explore-your-little-universe/blob/feat/serverless-react-litert-rag/mbti_lab/rag_seed.py)

## Neo4j lab — MBTI + 12 zodiac signs

The original graph lab remains available:

- [12 zodiac signs + MBTI graph](docs/ASTROLOGY_LAB.md)
- [Original MBTI web lab](mbti_lab/README.md)
- [Three-database collaboration plan](docs/THREE_DB_COLLAB_PLAN.md)

Use Python 3.12 and a dedicated local Neo4j database named `mbti-zodiac`. See [database separation](docs/DATABASE_SEPARATION.md) and the Korean README for setup. Connection settings stay in local, ignored files.

```cypher
MATCH p = (:MbtiType {code:'INTJ'})-[:HAS_TRAIT]->(:SharedTrait)
          <-[:HAS_TRAIT]-(:ZodiacSign {name:'물병자리'})
RETURN p;
```

The fictional content supports graph-learning and entertainment. It is not an official MBTI test, astrology forecast, compatibility score, diagnosis, or treatment recommendation.
