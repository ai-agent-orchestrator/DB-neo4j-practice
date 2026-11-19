# Neo4j GraphRAG — 조문 2개 연동 실습

- [MBTI Graph Lab — 마음의 지도](mbti_lab/README.md): MBTI 선택 → 성향·제안 그래프를 보여주는 로컬 웹앱. Neo4j 적재·조회 및 DB 없는 화면 미리보기 지원.

- [배달비 → Chunk → Document 반복 실습](docs/DELIVERY_LAB.md): Git으로 쿼리를 관리하고 Neo4j에 예시 데이터를 적재·조회한다. OpenAI 키 없이 실행 가능.

합성 조문 2개로 분할 → 비동기 적재 → Document 메타데이터 → Entity 근거 역추적을 검증한다. 실제 법령·환자 자료가 아닌 학습용 문장이다.

- [개발안과 공부할 포인트](docs/TWO_ARTICLE_MVP_PLAN.md)
- [단일 실행 스크립트](test_kg_pipeline.py)
- [3대 DB 협업 실험 개발안](docs/THREE_DB_COLLAB_PLAN.md): SQLite·Chroma·Neo4j 역할 분담, 합성 조건 필터·가격 계산·근거 추적 설계.

## 실행

Python 3.12와 로컬 Neo4j를 준비한다. Neo4j는 별도의 폐기 가능한 DB를 사용하며 이름에 `smoke`가 있어야 한다. 기본 DB가 `neo4j`인 Community 환경이라면 별도 로컬 인스턴스의 초기 DB를 `kg-smoke`로 구성한다. 기존 운영 인스턴스를 바꾸지 않는다.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
Copy-Item .env.example .env
# .env에 로컬 Neo4j 자격 증명, 사용 가능한 OpenAI 모델/API 키 설정
.venv/Scripts/python test_kg_pipeline.py --reset
```

`--reset`은 지정한 로컬 smoke DB의 `SmokeDocument`, `SmokeChunk`, `SmokeEntity` 라벨만 삭제한다. 해당 라벨은 이 실습 전용으로 예약한다. 다른 프로그램과 같은 smoke DB를 공유하거나 스크립트를 동시에 실행하지 않는다.

삭제 없는 재실행은 기존 실습 데이터가 있으면 실패한다. 이것은 중복을 감지하는 학습용 초기화 방식이며 운영용 upsert 멱등성 구현이 아니다.

성공 시 각 조문에 연결된 개체와 `[근거: 제1조 목적]`, `[근거: 제2조 정의]`, 마지막 `PASS`와 실측 시간이 출력된다. LLM 추출 내용은 달라질 수 있다. 10초·60줄·정확히 2회 호출을 보장하지 않는다. 임베딩과 LLM 호출은 유료일 수 있으며 SDK 내부 재시도도 발생할 수 있다.

## 검증 범위

로컬 검증은 라이브러리 API 호환성·대상 DB 보호·메타데이터/경로 판정 분기를 확인한다. 실제 E2E 성공은 로컬 Neo4j와 API 키를 설정하고 위 명령에서 `PASS`를 확인해야 한다. pytest 수집 시에는 외부 호출이 실행되지 않는다.
