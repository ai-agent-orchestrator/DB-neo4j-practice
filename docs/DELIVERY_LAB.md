# 배달비 출처 경로 반복 실습

Git은 쿼리와 실행 코드의 이력을 저장하고 Neo4j는 실행으로 생성한 노드와 관계를 저장한다. Git pull만으로 DB가 갱신되지는 않는다. 변경한 쿼리를 다시 실행한다.

합성 예시 문서 2개를 사용한다. 실제 법령이나 매장 정책이 아니다. 기존 Menu/Category 데이터는 수정하지 않는다. 위 예시 ID와 같은 노드는 갱신하며, `배달비` 개체가 이미 있으면 공유한다. 순차 재실행은 MERGE로 중복 생성을 방지한다. 동시 seed 실행은 피한다.

## 최초 설정 (저장소 루트의 PowerShell)

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
Copy-Item .env.delivery.example .env.delivery
```

`.env.delivery`에 Neo4j Desktop 인스턴스의 Bolt URI, 사용자, 비밀번호, DB 이름을 설정한다. 이 파일은 Git에서 제외된다. 기존 GraphRAG 실습의 `.env`와 별개이다. 운영체제 환경변수가 이미 있으면 그 값이 우선한다. 실행 시 출력되는 Database를 확인한다. Neo4j를 시작하고 해당 DB가 존재하는 상태에서 실행한다. OpenAI 키는 필요 없다.

## 반복 실행

```powershell
.venv/Scripts/python delivery_lab.py seed
.venv/Scripts/python delivery_lab.py query
.venv/Scripts/python delivery_lab.py query --keyword 배달
```

`cypher/delivery_seed.cypher`의 문장을 수정하고 seed를 재실행하면 같은 ID의 문서와 청크 내용이 갱신된다. ID를 추가하면 문서가 추가된다. ID를 파일에서 제거해도 DB의 기존 데이터는 자동 삭제되지 않는다. 조회 범위를 늘리려면 `cypher/delivery_paths.cypher`의 ID 목록도 수정한다.

## Browser에서 그래프로 보기

Browser에서 같은 DB를 선택한 뒤 다음 쿼리를 실행하고 Graph 보기를 선택한다.

```cypher
MATCH p = (e:__Entity__)-[:FROM_CHUNK]->(:Chunk)-[:FROM_DOCUMENT]->(d:Document)
WHERE e.name CONTAINS '배달비'
  AND d.id IN ['demo-delivery-doc-001', 'demo-delivery-doc-002']
RETURN p;
```

하나의 배달비 개체에서 두 청크를 거쳐 두 Document로 이어지는 경로가 보이면 성공이다. Python 없이 seed 파일 전체를 Browser에 붙여넣어도 적재할 수 있다.

## Git에 실험 기록 남기기

```powershell
git add cypher delivery_lab.py docs/DELIVERY_LAB.md
git commit -m "Update delivery provenance experiment"
git push
```

DB 데이터 파일과 비밀번호는 커밋하지 않는다. 새 환경에서는 설정 후 seed를 실행해 예시 그래프를 재현한다.
