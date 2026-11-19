# MBTI Graph Lab — 마음의 지도

16개 유형 선택 → Neo4j 조회 → 성향 카드와 SVG 관계 그래프. 외부 CDN, LLM, 유료 시각화 도구 없이 실행한다. 직접 작성한 재미용 콘텐츠이며 공식 검사나 의료 해석이 아니다.

## 실행 (저장소 루트)

```powershell
.venv/Scripts/python -m pip install -r requirements.txt
Copy-Item .env.mbti.example .env.mbti
# .env.mbti에 Neo4j 비밀번호와 실제 DB 이름 입력
.venv/Scripts/python -m mbti_lab.server --seed
```

http://127.0.0.1:8016 에 접속한다. 다음 실행부터는 `--seed`를 생략해도 된다. 문구 수정 후에는 `--seed`로 재적재한다. 기존 식당 데이터는 건드리지 않고 `MbtiType`, `MbtiTrait`, `MbtiInsight`, `MbtiSource` 라벨만 사용한다. MERGE는 순차 반복 적재 시 중복을 막으며 동시 적재는 피한다. 비밀번호는 Git에 포함되지 않는다.

DB 연결 전 화면만 확인하려면:

```powershell
.venv/Scripts/python -m mbti_lab.server --demo
```

데모 모드는 DB를 사용하지 않으며 화면에 명시된다. Neo4j 장애 시 자동으로 데모 결과로 바꾸지 않는다.

## Browser에서 확인

```cypher
MATCH p = (:MbtiType {code: 'INTJ'})-[:HAS_TRAIT]->(:MbtiTrait)
          -[:SUGGESTS]->(:MbtiInsight)-[:FROM_SOURCE]->(:MbtiSource)
RETURN p;
```

성향 8개와 제안 8개를 여러 유형이 공유한다. 원문 출처 노드는 직접 작성한 예시임을 표시한다. `data.py`를 수정하면 예시 문구를 변경할 수 있다. 초기 모델은 네 가지 선호의 조합이며, 유형별 고유한 심리 해석이나 검증된 성격 예측은 구현하지 않았다.

## 배포 범위

현재 서버는 로컬 실습용으로 127.0.0.1에만 바인딩한다. GitHub는 코드 저장소이며 여기 올리는 것만으로 Python/Neo4j가 실행되지는 않는다. GitHub Pages만으로 이 백엔드를 호스팅할 수 없다. 공개 배포 시에는 HTTPS와 운영용 웹서버, 서버 측 Neo4j 자격 증명, 접근 가능한 Neo4j 인스턴스를 갖춘 별도 백엔드 환경이 필요하다. 로컬 DB 포트를 인터넷에 직접 공개하지 않는다.

## 검증

```powershell
.venv/Scripts/python -m unittest discover -s mbti_lab -p "test_*.py"
```
