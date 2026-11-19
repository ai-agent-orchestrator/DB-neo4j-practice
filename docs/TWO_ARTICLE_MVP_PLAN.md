synthetic

# 조문 2개 단일 파일 MVP 개발안

2026-11-19 · 실제 자료 없는 학습·연동 실험

## 무엇을 확인하는가

35조문 대량 적재 전에 합성 제1조·제2조로 실제 SimpleKGPipeline 호출과 Neo4j 저장·조회가 이어지는지 확인한다. 분할·Semaphore(2)·run_async·Cypher를 `test_kg_pipeline.py` 한 파일에 둔다. 약 60줄에 맞추기보다 실패 시 원인을 알 수 있는 검사와 자원 정리를 우선한다. 10초는 실험 목표이며 서비스 지연·모델·재시도에 따라 달라진다.

## 구현 단계와 합격 기준

| 단계 | 구현 | 합격 기준 |
| --- | --- | --- |
| 사전 검사 | 환경변수·로컬 주소·smoke DB명 확인 | 기본/원격 DB 거부, 비밀값 출력 없음 |
| 초기화 | 명시적 --reset에서 실습 라벨만 삭제 | 전체 DB 삭제 없음; 삭제 없는 재실행은 기존 데이터 감지 |
| 조문 분할 | 조문별 입력 + FixedSizeSplitter(1000, 0) | 짧은 샘플 두 개가 각각 Chunk 1개로 저장 |
| 동시 적재 | 공유 Semaphore(2), 조문마다 파이프라인 생성 | 최대 2개 문서 실행; 실제 하위 API 전역 제한과 구분 |
| 메타데이터 | run_async(document_metadata=...) | Document 2개에 article_no/title/chapter 값 정확 |
| 역추적 | Entity → Chunk → Document | 두 조문 모두 개체 1개 이상과 정확한 근거 경로 |
| 결과 판정 | 개체 이름과 원문 대조, PASS/예외 | 빈 추출·메타데이터 누락·역방향 조회 오류는 실패 |
| 종료 | finally에서 driver.close | 성공·실패 모두 연결 반환 |

스키마를 명시해 자동 스키마 추출 단계를 피하고, entity resolution을 꺼서 이름 기반 병합에 따른 혼선을 줄인다. 실습 라벨은 SmokeEntity/SmokeChunk/SmokeDocument를 사용하며 관계는 기본값을 유지한다. 공개 문서의 일반 Entity 라벨과 혼동하지 않는다.

## 공부할 포인트 12가지

### 1. 초기화와 멱등성은 다르다

`MATCH (n) DETACH DELETE n`은 모든 노드를 지우는 명령이다. 재실행해 겹치지 않는 이유는 삭제했기 때문이며 멱등 upsert를 검증한 것이 아니다. 실습은 라벨 범위로 삭제한다. 운영 확장은 문서 판본·원문 해시·결정적 Chunk ID·고유 제약·MERGE로 바꾸고 삭제 없이 10회 실행해 논리 개체 수가 유지되는지 확인한다.

### 2. 메타데이터는 모델 추출 결과와 별개다

article_no/title/chapter는 Python이 document_metadata로 전달하는 출처 정보다. LLM이 이 값을 추측하게 하지 않는다. 잘못된 메타데이터도 그대로 저장될 수 있으므로 원본 조문과 값이 일치하는지 검증한다. 이번 실습은 조문 하나를 Document 하나로 보지만 실제 규정집은 Document 1개·Article 여러 개 구조가 더 적합할 수 있다.

### 3. 관계 방향을 화살표로 읽는다

```cypher
MATCH (e:SmokeEntity)-[:FROM_CHUNK]->(c:SmokeChunk)
      -[:FROM_DOCUMENT]->(d:SmokeDocument)
RETURN e.name, c.text, d.article_no, d.title, d.chapter;
```

역추적은 Entity → Chunk → Document다. 브라우저에서 Document를 시작점으로 보려면 화살표를 반대로 읽는다.

```cypher
MATCH p=(d:SmokeDocument)<-[:FROM_DOCUMENT]-(c:SmokeChunk)
        <-[:FROM_CHUNK]-(e:SmokeEntity)
RETURN p;
```

관계명을 바꾸는 LexicalGraphConfig를 사용하면 조회도 같이 바꿔야 한다. 값이 없을 때 방향을 생략해 억지로 성공시키지 않는다.

### 4. 노드 수와 근거 경로를 함께 본다

Document만 생겼다고 추출 성공이 아니다. Document 2개, Chunk 2개, 조문별 개체 경로를 각각 검사한다. 다음 쿼리로 먼저 메타데이터를 확인한다.

```cypher
MATCH (d:SmokeDocument)
RETURN d.article_no, d.title, d.chapter;
```

개체 수는 생성 모델에 따라 달라지므로 특정 개수를 강제하지 않는다. 개체가 아예 없거나 이름이 원문에 없으면 이 실습에서는 실패 처리한다. 이 문자열 검사는 일반적인 의미 정확성 평가를 대신하지 않는다.

### 5. gather는 병렬 실행 요청, Semaphore는 실행 구간 제한

gather가 여러 코루틴을 기다리고 Semaphore가 감싼 문서 실행을 2개로 제한한다. 잠금 대상을 매 호출마다 새로 만들면 공유 제한이 되지 않는다. 문서 2개만 있으므로 Semaphore 제한 효과를 성능으로 입증하지는 않는다. 35개 확장 시 큐와 내부 LLM·임베딩 호출별 제한기를 별도로 둔다.

### 6. await가 있어도 내부 작업이 모두 비동기는 아니다

SimpleKGPipeline의 driver 타입과 실제 하위 구현을 확인한다. 여기서는 라이브러리가 받는 동기 Driver를 사용하고 직접 실행하는 DB 쿼리는 asyncio.to_thread로 이벤트 루프 밖에 둔다. 모든 I/O가 완전 비동기라고 표현하지 않는다. 동시에 파이프라인 인스턴스를 공유하지 않는다.

### 7. 조문 수·청크 수·호출 수는 다르다

조문이 길면 여러 청크가 된다. 자동 스키마 추출·임베딩·재시도도 호출을 늘린다. 이번 실습은 짧은 조문·고정 스키마·겹침 없는 청킹으로 줄이지만 실제 호출과 비용은 제공자 사용량으로 확인해야 한다. 타임아웃은 이미 발생한 비용을 취소하지 않는다.

### 8. 빈 결과를 성공으로 오인하지 않는다

on_error='RAISE'는 추출 오류를 드러내지만 모든 논리적 빈 결과를 막아주는 것은 아니다. 두 조문 각각에서 경로가 조회되는지 후속 검사한다. 스키마·모델 출력·프롬프트를 점검하고 결과를 확인 없이 재호출하지 않는다.

### 9. 부분 실패는 남을 수 있다

한 조문 성공·다른 조문 실패 시 이미 저장된 노드는 남을 수 있다. gather(return_exceptions=True)로 결과를 모두 기다리고 하나라도 실패하면 PASS를 내지 않는다. 다음 실습에서 --reset으로 정리한다. 타임아웃·취소 시도 부분 결과가 남을 수 있다. 운영은 작업 상태·체크포인트·검수 영역·승인 후 게시로 확장한다.

### 10. 고정 모델 설정도 완전 재현성을 보장하지 않는다

temperature=0과 고정 패키지 버전은 변동을 줄일 뿐이다. 모델별로 temperature/JSON 응답 지원이 다를 수 있으므로 사용 가능한 모델을 설정한다. 샘플·설정·모델·라이브러리 버전·실행 시간을 기록한다. 실제 지식 정답 평가는 별도 골든셋이 필요하다.

### 11. 출력 근거와 답변 정확성은 별개다

`[근거: 제1조 목적]`은 저장된 연결을 확인한 것이다. 원문이 사실인지, 관계 의미가 맞는지, 예외가 빠졌는지는 추가 검수 대상이다. retrieval_hit은 문서·판본·조문을 함께 비교하고, 복수 근거 누락은 recall로 별도 평가한다.

### 12. 비밀값과 실행 대상이 먼저다

.env는 Git에서 제외한다. 저장소에는 실제 API 키·DB 암호·환자 자료를 넣지 않는다. localhost와 DB명 검사는 실수 방지 장치이며 DB 전용 계정 권한을 대신하지 않는다. 로컬 포트가 운영 서버로 터널링되지 않았는지도 사용자가 확인한다. 실습 전용 인스턴스를 공유하지 않는다.

## 확장 순서

2개 조문 PASS → 삭제 없는 멱등 키 설계 → 35개 합성 조문 → 요청/토큰·예산 제한 → 장애·재실행 검증 → 규정집 파서·판본·원문 좌표 → 전문가 검수. 데이터만 35개로 늘리고 Semaphore(5)로 바꾸는 것을 운영 준비 완료로 간주하지 않는다.

## 공식 참고

- [Neo4j KG Builder](https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_kg_builder.html)
- [run_async와 LexicalGraphConfig API](https://neo4j.com/docs/neo4j-graphrag-python/current/api.html)
- [Python gather·timeout](https://docs.python.org/3/library/asyncio-task.html)
- [Python Semaphore](https://docs.python.org/3/library/asyncio-sync.html)
