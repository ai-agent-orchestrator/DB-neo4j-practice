# Neo4j 실습 — MBTI + 12별자리 그래프

MBTI와 12별자리를 공통 성향으로 연결하고 Neo4j에서 관계를 탐색하는 학습용 프로젝트다. 콘텐츠는 직접 작성한 재미용 예시이며 공식 성격 검사나 진단, 검증된 점성술 해석이 아니다. LLM이나 OpenAI API 없이 실행할 수 있다.

- [12별자리 + MBTI 그래프](docs/ASTROLOGY_LAB.md): 별자리 12개를 공통 성향으로 연결하고 Neo4j Browser에서 확인한다.
- [MBTI Graph Lab — 마음의 지도](mbti_lab/README.md): MBTI 선택 → 성향·제안 그래프를 보여주는 로컬 웹앱. Neo4j 적재·조회 및 DB 없는 화면 미리보기 지원.
- [3대 DB 협업 실험 개발안](docs/THREE_DB_COLLAB_PLAN.md): SQLite·Chroma·Neo4j 역할 분담, 합성 조건 필터·가격 계산·근거 추적 설계.

## 실행

Python 3.12와 로컬 Neo4j를 준비하고 전용 데이터베이스 `mbti-zodiac`를 생성한다. DB 생성과 기존 데이터 분리는 [데이터베이스 분리 안내](docs/DATABASE_SEPARATION.md)를 참고한다.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
Copy-Item .env.mbti.example .env.mbti
# .env.mbti에 Neo4j URI, 사용자 이름, 비밀번호 설정. DB는 mbti-zodiac 고정
.venv/Scripts/python -m mbti_lab.astrology
.venv/Scripts/python -m mbti_lab.server
```

웹앱: http://127.0.0.1:8016

별자리 적재 명령은 MBTI 데이터도 함께 준비한다. 순차 재실행은 같은 노드와 관계를 재사용한다. 비밀번호가 들어 있는 `.env.mbti`는 Git에서 제외된다.

Neo4j 없이 화면만 미리 보려면:

```powershell
.venv/Scripts/python -m mbti_lab.server --demo
```

## Neo4j Browser에서 그래프 확인

`mbti-zodiac` DB를 선택한 뒤 실행하고 Graph 보기로 전환한다.

```cypher
MATCH p = (:MbtiType {code:'INTJ'})-[:HAS_TRAIT]->(:SharedTrait)
          <-[:HAS_TRAIT]-(:ZodiacSign {name:'물병자리'})
RETURN p;
```

웹앱은 MBTI 선택 화면을 제공하며, 별자리 연결은 현재 Neo4j Browser에서 탐색한다. GitHub는 코드와 예시 데이터 정의를 보관하며 웹앱 서버나 Neo4j를 자동 실행하지 않는다.

## 검증

```powershell
.venv/Scripts/python -m unittest discover -s mbti_lab -p "test_*.py"
.venv/Scripts/python -m mbti_lab.verify_http
```
