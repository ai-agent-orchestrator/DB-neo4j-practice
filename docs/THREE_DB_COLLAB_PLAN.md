synthetic

# 3대 DB 협업 체험 — 최소 실험 개발안

2026-11-19 · 설계 초안 · 예정 파일: `demo_3db_collab.py`

## 1. 목적과 실험 범위

SQLite·Chroma·Neo4j가 서로 다른 판단을 담당하고 공통 ID로 결과를 연결하는 과정을 체험한다. 기존 [조문 2개 실습](TWO_ARTICLE_MVP_PLAN.md) 다음 단계다. 이번 변경은 개발안이며 실행 스크립트를 구현하거나 실제 3DB 연동을 검증한 것은 아니다.

질문은 “합성 조건 P가 있는 사용자의 두통 관련 후보 중, 실험 규칙을 통과하고 재고가 있는 가장 저렴한 상품은?”으로 고정한다. 원안의 임신·신장질환 시나리오는 구조만 가져오고, 실제 상품명·성분별 금기·복용량·처방 권고로 해석될 정보는 사용하지 않는다. P·K는 각각 임신·신장질환 같은 조건 분기를 설명하기 위한 가상 코드이며 실제 임상 규칙과 대응하지 않는다.

**성공의 의미는 지정된 합성 데이터에서 후보 검색 → 규칙 확인 → 가격 계산 → 출처 연결이 맞는다는 것이다. 환각 없는 의료 답변이나 안전한 약품 추천을 보장하지 않는다.** 실제 의료 기능은 별도 근거·규제·전문의 검토가 필요하다.

## 2. 원안의 보완점

| 원안 | 실험 설계 기준 |
| --- | --- |
| Vector 단독은 반드시 실패 | 벡터는 관련도 후보를 반환한다. 금지·미확인 후보가 섞일 수 있음을 관찰하며 실패 순위를 강제로 만들지 않는다. |
| NOT EXISTS면 안전 | 금기 경로 부재는 데이터 누락일 수도 있다. 조건별 검토 완료·성분 매핑 완전성을 먼저 확인한다. |
| 최저가 약품 | 검색 후보 중 최저가인지 전체 상품 중 최저가인지 구분한다. 기본 실험은 4종 모두 후보로 회수한다. |
| 10건이면 모든 데이터 | 상품 4건·안내문 4건 중심의 작은 데이터다. 그래프 노드·관계·검토 기록까지 합치면 10건을 넘는다. |
| 설정 없이 15분 | Neo4j 준비·패키지 설치·임베딩 모델 다운로드가 끝난 뒤 15분 체험을 목표로 한다. |

## 3. DB별 책임과 공통 계약

| 저장소 | 최소 데이터 | 책임 | 담당하지 않는 것 |
| --- | --- | --- | --- |
| SQLite `:memory:` | 상품 4종의 ID·이름·동일 단위 가격·재고 | 정확한 수치·정렬·현재 실험 재고 | 의미 검색·금기 판단 |
| Chroma EphemeralClient | 상품별 합성 안내문 4개·출처·버전·drug_id | 증상 관련 후보·주의 문구 원문 검색 | 금기 확정·가격 계산 |
| Neo4j 전용 로컬 smoke DB | 상품·성분·조건·검토 상태·차단 규칙 | 조건별 차단과 미확인 분기·근거 경로 | 실시간 가격·임상 안전 보증 |
| Python 오케스트레이터 | 단계별 결과·공통 ID·dataset_version | 교집합·누락 검사·템플릿 출력 | 모델의 추측으로 빈 결과 보완 |

모든 저장소는 `dataset_id=three-db-v1`, `dataset_version=v1`, `drug_id=D1..D4`를 공유한다. 표시 이름 대신 ID로 조인하고 ID 중복·누락·버전 불일치는 실패 처리한다. RDB 가격은 모두 동일한 합성 판매 단위·통화로 설정해 가격 비교 조건을 맞춘다. 상담 로그는 핵심 학습에 필요 없으므로 MVP에서 제외한다.

## 4. 합성 데이터 명세

다음 규칙은 실습용으로 지어낸 것이며 약리학적 사실이 아니다.

| ID | 상품명 | 성분 | 가격(가상 원) | 재고 | P 검토 | K 검토 |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | 합성진통-A | I1 | 1200 | 5 | 검토 완료·차단 없음 | 검토 완료·차단 없음 |
| D2 | 합성진통-B | I2 | 500 | 8 | 검토 완료·차단 | 검토 완료·차단 없음 |
| D3 | 합성진통-C | I3 | 800 | 0 | 검토 완료·차단 없음 | 검토 완료·차단 |
| D4 | 합성진통-D | I4 | 300 | 9 | 미검토 | 미검토 |

Chroma에는 각 상품의 “두통 관련 합성 안내” 한 문단과 주의 문구·source_id를 넣는다. D2에는 “조건 P에서는 실험 규칙상 제외”를 명시하고, D4에는 “조건별 검토 미완료”를 명시한다. 벡터가 금지 문서를 상위로 반환하더라도 그것은 복용 추천이 아니라 관련 문서 검색 결과다.

그래프 모델:

```text
(:DemoDrug)-[:CONTAINS]->(:DemoIngredient)
(:DemoIngredient)-[:CONTRAINDICATED_FOR {source_id, version}]->(:DemoCondition)
(:DemoDrug)-[:REVIEWED_FOR {status:'COMPLETE', version}]->(:DemoCondition)
```

Drug에는 expected_ingredient_count=1을 기록한다. 이번 실험은 단일 성분만 사용하며, 실제 복합제는 모든 성분과 조건별 검토가 완전해야 한다. REVIEWED_FOR는 위 합성 규칙 집합의 검토 상태이며 임상 승인이나 실제 안전성 확인이 아니다.

## 5. 단일 스크립트 구현 명세

예정 함수: `validate_config`, `seed_sqlite`, `seed_chroma`, `seed_graph`, `search_candidates`, `classify_graph_candidates`, `select_cheapest`, `render_trace`, `main`.

1. 로컬 주소·명시적 smoke DB명·실습 권한을 확인한다. `--condition P` 기본값, 선택값 K, P+K를 지원한다.
2. 공통 합성 fixture를 만들고 ID·판본·가격 단위·성분 수를 검증한다.
3. SQLite 메모리 DB와 Chroma 임시 컬렉션에 적재하고 Neo4j에는 실습 라벨·dataset_id 범위에서 고유 키와 MERGE로 적재한다.
4. 같은 질문을 Chroma에 질의해 후보 ID·관련도 또는 거리·원문을 출력한다. 기본 k=4로 전체 후보를 회수한다.
5. Neo4j에서 후보마다 BLOCKED / UNKNOWN / RULE_PASS를 반환한다. BLOCKED는 차단 근거 경로를, UNKNOWN은 검토·매핑 부족 이유를 기록한다.
6. RULE_PASS ID만 SQLite에 전달한다. 재고 양수 중 가격·ID 순으로 한 건 선택한다.
7. 선택 상품의 Vector 원문과 Graph 검토 근거·차단 부재의 적용 범위, RDB 가격·재고를 고정 템플릿으로 출력한다.
8. 연결·임시 자원을 finally로 정리하고 실행시간·후보 수·통과/제외/미확인 수를 기록한다.

Chroma는 로컬 임베딩을 사용하며 문서와 질문에 동일한 모델을 적용한다. 기본 모델의 한국어 검색 품질을 가정하지 않고 fixture 회수 결과를 확인한다. 최초 다운로드는 준비 시간에 포함한다. 필요하면 한국어 지원 모델을 별도로 고정하고 의존성을 기록한다. 수작업 임베딩은 DB 연결 검증 전용으로 명시하며 의미 검색 성능 실험으로 표현하지 않는다. [Chroma 임베딩 문서](https://docs.trychroma.com/docs/embeddings/embedding-functions)

LLM은 사용하지 않는다. 질문→증상·조건 해석은 고정 데모 입력과 CLI 인자로 처리하고, 최종 응답은 템플릿으로 만든다. 환경에 OpenAI 키가 있어도 호출하지 않는다. 비용은 로컬 모델 다운로드·CPU·메모리·Neo4j 운영 자원으로 구분한다.

## 6. Graph 필터와 미확인 처리

다음 Cypher는 조건 P 하나에 대한 통과 쿼리 명세다. 전제: 조인할 모든 노드에 동일 dataset_id/version이 있고 성분 매핑이 검증됐다. 실제 구현 시 동일 판본 조건을 노드·관계 조회에 일관되게 적용한다.

```cypher
MATCH (d:DemoDrug {dataset_id: $dataset_id, version: $version})
WHERE d.drug_id IN $candidate_ids
  AND d.expected_ingredient_count = 1
  AND COUNT {
    MATCH (d)-[:CONTAINS]->(i:DemoIngredient)
    WHERE i.dataset_id = $dataset_id AND i.version = $version
  } = 1
  AND EXISTS {
    MATCH (d)-[r:REVIEWED_FOR]->(c:DemoCondition)
    WHERE c.code = $condition AND c.dataset_id = $dataset_id
      AND c.version = $version AND r.status = 'COMPLETE'
      AND r.version = $version
  }
  AND NOT EXISTS {
    MATCH (d)-[:CONTAINS]->(:DemoIngredient)
          -[r:CONTRAINDICATED_FOR]->(c:DemoCondition)
    WHERE c.code = $condition AND c.dataset_id = $dataset_id
      AND c.version = $version AND r.version = $version
  }
RETURN d.drug_id AS drug_id;
```

`NOT EXISTS`는 일치하는 경로가 없다는 뜻이다. 긍정적인 안전 경로를 만들어낸 것으로 표현하지 않는다. 차단 후보는 실제 contraindication 경로를, 통과 후보는 검토 상태·성분 목록·확인한 조건·규칙 버전을 보여준다. 미검토·누락 후보는 UNKNOWN으로 보류한다. 동시 다중 조건은 모든 조건의 검토 완료를 요구하고 어느 하나라도 차단되면 제외한다. [Neo4j EXISTS 문서](https://neo4j.com/docs/cypher-manual/current/subqueries/existential/)

## 7. SQLite 가격 선택과 최저가 범위

```sql
SELECT id, name, price, stock
FROM drugs
WHERE id IN (?, ?) AND stock > 0
ORDER BY price ASC, id ASC
LIMIT 1;
```

물음표 개수는 허용 ID 수에 맞춰 만들고 값은 파라미터로 전달한다. ID가 0개면 SQL을 실행하지 않고 후보 없음으로 종료한다. 재고는 조회 시점의 값이며 예약·구매 확정이 아니다. top-k를 줄이면 “검색된 후보 중 최저가”라고 출력하고 전체 최저가를 주장하지 않는다. 실습 4종·k=4에서만 전체 합성 상품 범위를 비교한다.

## 8. 비교 실험 예상 출력

```text
[합성 데이터 / 실제 복약 안내 아님]
A. Vector 단독
  D1, D2, D3, D4의 실제 검색 순위·거리·원문 표시
  가격/재고/조건 충족을 확정할 수 없음

B. 3DB 협업, condition=P
  Vector: 4개 후보
  Graph: D2 BLOCKED(규칙 경로), D4 UNKNOWN(미검토)
         D1/D3 RULE_PASS(지정된 합성 규칙 범위)
  SQLite: D3 재고 0 제외 → D1 1200 가상 원 선택
  원문: D1 안내문 source_id + version
  근거: I1 성분 확인 + P 검토 완료 + P 차단 경로 미검출
  결과: 실험 규칙을 통과한 재고 상품 중 최저가 D1
```

K만 입력하면 D2, P+K이면 D1이 선택된다. 순위는 임베딩에 따라 달라질 수 있지만 k=4로 네 후보를 모두 회수하면 합성 규칙과 가격에 따른 결과는 같다. 모든 후보가 제외·미확인이면 추천을 만들지 않고 자료 부족/해당 후보 없음으로 출력한다.

## 9. 초기화·멱등성·DB 간 불일치

SQLite/Chroma는 프로세스마다 새 메모리 저장소를 만든다. Neo4j는 실습 전용 라벨과 dataset_id/version 포함 고유 키로 MERGE한다. 변경 시 fixture 판본을 올리고 새 판본만 검색한다. `--reset`은 해당 dataset_id와 실습 라벨 범위로 제한하며 전체 DB 삭제는 금지한다.

세 DB에 분산 트랜잭션이 있다고 가정하지 않는다. 적재가 모두 끝난 뒤 ID 집합·판본·원문 출처·성분 매핑을 대조하고 READY로 전환한다. 하나라도 실패하면 실험 실행을 중단한다. 운영 확장은 manifest·작업 상태·재시도·승인 후 활성 판본 전환이 필요하다.

## 10. 15분 수업 진행안과 준비물

사전 준비: Python 3.12, 전용 로컬 Neo4j smoke DB, Chroma 패키지와 임베딩 모델 캐시, 네트워크/DB 권한 확인. 최종 버전은 구현 시 고정하고 기존 조문 실습 의존성 파일과 분리한다. 모델 다운로드가 필요하면 오프라인 15분 실행을 약속하지 않는다.

| 시간 | 학생이 하는 일 |
| --- | --- |
| 0~3분 | 4종 fixture와 세 DB의 공통 ID 확인 |
| 3~6분 | Vector 순위·안내문 확인; 순위와 허용 여부의 차이 설명 |
| 6~9분 | P 필터 적용; D2 차단과 D4 미확인 이유 확인 |
| 9~12분 | D3 재고 0 확인; RDB 최저가·최종 출처 출력 |
| 12~15분 | K/P+K 변경, D1 품절·D4 검토 누락 실험 |

## 11. 인수 테스트와 공부할 포인트

- 기본 P → D1, K → D2, P+K → D1 결과를 ID로 단언한다.
- D1 재고를 0으로 바꾸면 P 결과가 후보 없음으로 바뀌는지 확인한다.
- D4가 가장 싸더라도 미검토면 선택되지 않아야 한다.
- 성분 엣지·조건 노드·검토 상태를 제거하면 UNKNOWN이며 통과로 바뀌면 안 된다.
- 모든 후보 차단·미확인·품절과 빈 Vector 결과에서 예외 없이 명시적으로 보류한다.
- ID/판본 불일치 시 실행 중단을 확인한다. 재적재 후 논리 노드·관계 중복이 없어야 한다.
- 각 제외 사유와 최종 원문·검토 근거를 출력하고 실제 DB 조회 결과로 검증한다.
- top-k 축소 시 후보 누락과 전체 최저가 주장의 차이를 확인한다.
- Vector 단독 순위를 조작하거나 항상 오답이라고 단언하지 않는다. 필터 가능한 메타데이터를 가진 Vector/RDB도 규칙을 구현할 수 있으며 Graph의 가치는 관계·근거 추적과 유지보수에서 평가한다.
- 합성 규칙 성공, 검색 품질, 임상 안전성은 서로 다른 검증 대상이다.

## 12. 완료 산출물

후속 구현: `demo_3db_collab.py` 단일 실행 파일, 별도 3DB 의존성 목록, 비밀값 없는 환경 예시, 실행 명령, 실제 단계별 출력과 장애 테스트 기록. DB 연결이 없는 모의 검증 결과와 실제 3DB E2E 결과는 나눠 기록한다. 이 개발안 단계에서는 성능·E2E 성공을 주장하지 않는다.
