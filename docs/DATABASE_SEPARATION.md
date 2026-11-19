# MBTI·별자리 전용 DB

- 논리 프로젝트 이름: `mbti-zodiac` (MBTI·별자리 그래프)
- 식당 DB: `ohgirestaurant-graph`
- MBTI·별자리 DB: `mbti-zodiac`

Neo4j Desktop의 프로젝트 표시 이름과 실제 DB 이름은 별개다. 같은 로컬 인스턴스 안에서 실제 DB를 분리한다. 프로젝트 표시 이름만 바꿔서는 데이터가 분리되지 않는다.

## 새 환경

다중 DB를 지원하는 Neo4j와 DB 생성 권한이 필요하다. `system` DB에서 다음을 실행한다.

```cypher
CREATE DATABASE `mbti-zodiac` IF NOT EXISTS WAIT;
```

`.env.mbti.example`을 `.env.mbti`로 복사하고 비밀번호를 설정한다. `NEO4J_DATABASE=mbti-zodiac`를 유지한다. 별자리 적재 명령은 MBTI도 함께 준비한다.

```powershell
.venv/Scripts/python -m mbti_lab.astrology
.venv/Scripts/python -m mbti_lab.server
```

Neo4j Browser에서는 `:use mbti-zodiac`를 실행한다. 환경변수에 기존 DB 설정이 남아 있다면 제거하거나 `mbti-zodiac`로 바꾼다. 이미 실행 중인 서버는 재시작해야 한다.

## 기존 혼합 DB 이전

실행 중인 실습 서버와 다른 적재 작업을 중지한 뒤 실행한다. `.env.mbti`의 자격 증명을 사용하며 원본은 `ohgirestaurant-graph`, 대상은 `mbti-zodiac`로 고정한다.

```powershell
.venv/Scripts/python -m mbti_lab.migrate_database
```

이 명령은 실습 전용 7개 라벨의 노드와 관계를 `backups/`의 JSON에 보관한다. 외부 노드와 연결된 경우 중단한다. 빈 대상 DB에 속성·라벨·관계를 복사하고 내용을 검증한 후 원본의 해당 노드만 삭제한다. 나머지 노드 수를 확인한 뒤 로컬 `.env.mbti`를 갱신한다. 비밀번호와 백업은 Git에 올리지 않는다.

대상 DB가 비어 있지 않으면 원본을 삭제하지 않고 중단한다. 이미 이전된 환경에서 재실행하지 않는다. 복사 후 정리에 실패하면 양쪽 데이터와 백업을 확인하고 수동 복구한다. 다른 적재 작업과 동시에 실행하지 않는다. JSON 백업은 이 실습의 문자열·숫자 속성용이며 Neo4j 전체 DB 덤프가 아니다.

## 데이터 모델과 다음 단계

현재는 정형 MBTI 데이터와 정형 별자리 데이터를 공통 `SharedTrait` 노드로 연결한다.

```text
MbtiType → SharedTrait ← ZodiacSign
                 ↓
            MbtiInsight
```

다음 확장 후보는 비정형 소개 글을 Document·Chunk로 저장하고 성향을 추출해 `SharedTrait`에 연결하는 것이다. 원문 출처와 추출 근거를 남기는 단계까지 포함한다. 아직 비정형 처리 기능은 구현하지 않았다.
