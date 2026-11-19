"""synthetic: two-article integration smoke test; never use production data."""
import argparse
import asyncio
import os
import time
from urllib.parse import urlparse

ARTICLES = [
    {"article_no": "제1조", "title": "목적", "chapter": "총칙",
     "text": "제1조 목적: 가상기관은 문서관리로 기록보존을 지원한다."},
    {"article_no": "제2조", "title": "정의", "chapter": "총칙",
     "text": "제2조 정의: 가상기록은 합성문서를 뜻한다."},
]
LABELS = ("SmokeDocument", "SmokeChunk", "SmokeEntity")


def validate_target(uri, database):
    """Allow only an explicit local smoke database, even when --reset is absent."""
    if urlparse(uri).hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Only a local disposable Neo4j target is allowed")
    if "smoke" not in database.lower() or database.lower() in {"system", "neo4j"}:
        raise ValueError("NEO4J_DATABASE must explicitly name a dedicated smoke database")


async def run(reset):
    from dotenv import load_dotenv
    from neo4j import GraphDatabase
    from neo4j_graphrag.components.text_splitters.fixed_size_splitter import FixedSizeSplitter
    from neo4j_graphrag.components.types import LexicalGraphConfig
    from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
    from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
    from neo4j_graphrag.llm import OpenAILLM

    load_dotenv()
    required = ("NEO4J_URI", "NEO4J_DATABASE", "NEO4J_PASSWORD",
                "OPENAI_API_KEY", "OPENAI_MODEL")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError("Missing environment variables: " + ", ".join(missing))
    uri, database = os.environ["NEO4J_URI"], os.environ["NEO4J_DATABASE"]
    validate_target(uri, database)
    driver = GraphDatabase.driver(uri, auth=(os.getenv("NEO4J_USERNAME", "neo4j"),
                                            os.environ["NEO4J_PASSWORD"]))

    # SimpleKGPipeline uses a synchronous driver; move our direct queries off-loop.
    async def query(cypher, **params):
        result = await asyncio.to_thread(driver.execute_query, cypher,
                                         parameters_=params, database_=database)
        return [record.data() for record in result.records]

    started = time.perf_counter()
    try:
        await asyncio.to_thread(driver.verify_connectivity)
        if reset:
            await query("MATCH (n) WHERE any(label IN labels(n) WHERE label IN $labels) "
                        "DETACH DELETE n", labels=list(LABELS))
        existing = await query("MATCH (n) WHERE any(label IN labels(n) WHERE label IN $labels) "
                               "RETURN count(n) AS count", labels=list(LABELS))
        if existing[0]["count"]:
            raise ValueError("Existing smoke data: rerun with --reset or use a fresh smoke DB")

        slots = asyncio.Semaphore(2)

        async def ingest(article):
            async with slots:
                pipeline = SimpleKGPipeline(
                    llm=OpenAILLM(model_name=os.environ["OPENAI_MODEL"],
                                  model_params={"temperature": 0,
                                                "response_format": {"type": "json_object"}}),
                    driver=driver,
                    embedder=OpenAIEmbeddings(model=os.getenv(
                        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")),
                    from_file=False, on_error="RAISE",
                    perform_entity_resolution=False, neo4j_database=database,
                    text_splitter=FixedSizeSplitter(chunk_size=1000, chunk_overlap=0),
                    lexical_graph_config=LexicalGraphConfig(
                        document_node_label="SmokeDocument", chunk_node_label="SmokeChunk"),
                    schema={"node_types": [{"label": "SmokeEntity",
                             "properties": [{"name": "name", "type": "STRING"}]}],
                            "relationship_types": [], "patterns": [],
                            "additional_node_types": False},
                )
                await pipeline.run_async(
                    text=article["text"],
                    document_metadata={key: value for key, value in article.items() if key != "text"},
                )

        # A global timeout prevents an indefinite smoke run; it is not a cost cap.
        async with asyncio.timeout(float(os.getenv("SMOKE_TIMEOUT_SECONDS", "120"))):
            results = await asyncio.gather(*(ingest(a) for a in ARTICLES), return_exceptions=True)
        failures = [r for r in results if isinstance(r, BaseException)]
        if failures:
            raise RuntimeError(f"{len(failures)} article(s) failed; reset partial smoke data") from failures[0]

        documents = await query(
            "MATCH (d:SmokeDocument) OPTIONAL MATCH (c:SmokeChunk)-[:FROM_DOCUMENT]->(d) "
            "RETURN d.article_no AS article_no, d.title AS title, d.chapter AS chapter, "
            "count(c) AS chunks ORDER BY article_no")
        expected = {(a["article_no"], a["title"], a["chapter"]) for a in ARTICLES}
        actual = {(d["article_no"], d["title"], d["chapter"]) for d in documents}
        if len(documents) != 2 or actual != expected or any(d["chunks"] != 1 for d in documents):
            raise AssertionError(f"Document metadata/chunk verification failed: {documents}")
        rows = await query(
            "MATCH (e:SmokeEntity)-[:FROM_CHUNK]->(c:SmokeChunk)-[:FROM_DOCUMENT]->(d:SmokeDocument) "
            "RETURN e.name AS entity, c.text AS text, d.article_no AS article_no, "
            "d.title AS title ORDER BY article_no, entity")
        if {row["article_no"] for row in rows} != {a["article_no"] for a in ARTICLES}:
            raise AssertionError("Both articles must have at least one entity provenance path")
        for row in rows:
            if not row["entity"] or row["entity"] not in row["text"]:
                raise AssertionError("Entity name must appear in its source chunk for this fixture")
            print(f"{row['entity']} [근거: {row['article_no']} {row['title']}]")
        print(f"PASS: 2 documents, 2 chunks, {len(rows)} paths; {time.perf_counter()-started:.2f}s")
    finally:
        await asyncio.to_thread(driver.close)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="Delete only Smoke* nodes in the local smoke DB")
    args = parser.parse_args()
    asyncio.run(run(args.reset))
