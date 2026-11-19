# 검증 기록

2026-11-19 · Python 3.12 · requirements.txt 버전 기준

- 설치된 SimpleKGPipeline/LexicalGraphConfig/OpenAILLM/OpenAIEmbeddings 생성자와 run_async 인자 호환성 확인.
- CLI `--help` 정상 출력; import만으로 외부 API 실행 없음.
- 외부 API·DB·버전 조회를 모의 처리한 성공 경로에서 두 조문 메타데이터 전달과 근거 출력 확인.
- 원격 주소·기본 DB 거부 확인.
- 제2조 근거 경로 누락 시 AssertionError 확인.
- 성공·실패에서 드라이버 close 확인.

모의 테스트 출력의 시간과 PASS는 실제 E2E 성능 실적이 아니다. 실제 Neo4j 저장·삭제·Cypher 실행 및 모델 호출은 자격 증명과 서버가 준비되지 않아 수행하지 않았다. 사용자 환경에서 README 실행 명령으로 확인해야 한다. 문서의 10초 목표는 검증되지 않았다.
