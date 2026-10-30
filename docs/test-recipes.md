# Python과 JavaScript 검사 연결

하네스의 검사 종류는 `unittest`, `json`, `command`입니다. 아래 항목은 `.harness/contract.json`의 `checks` 배열에 넣는 **예시**입니다. 실제 과제에서는 요구 원문에서 기대값을 먼저 정하고, 해당 검사 ID를 요구와 계획의 작업에 연결합니다. 계획 승인 뒤 `python3 .harness-kit/hx.py --root . check --id C1`로 실행합니다. 직접 설치하지 않았다면 툴킷의 `hx.py` 경로를 사용합니다.

## Python

표준 라이브러리의 `unittest`는 정확한 테스트 이름을 지정합니다. 다음 예시는 `tests/test_math.py`에 `MathTests.test_sum`이 있을 때 사용합니다.

```json
{"id":"C1","kind":"unittest","test_dir":"tests","tests":["test_math.MathTests.test_sum"],"tracked_paths":["src","tests"],"timeout_seconds":30}
```

프로젝트에 `pytest`가 이미 설치되어 있다면 다음 명령을 `command`로 연결할 수 있습니다. 이 예시는 **실행하지 않았습니다**. `pytest` 설치도 수행하지 않았습니다. `command`는 테스트 명령의 종료 상태만 기록하므로, 요구의 `verification: "behavior"`에는 `unittest` 또는 `json` 검사를 추가합니다.

```json
{"id":"C_PYTEST","kind":"command","argv":["{python}","-m","pytest","-q"],"tracked_paths":["src","tests","pyproject.toml"],"timeout_seconds":60}
```

Python 프로그램이 표준 출력에 JSON 하나를 쓴다면 `json`으로 독립적인 기대값을 비교할 수 있습니다. 다음 명령과 파일 경로는 **실행하지 않은 예시**입니다.

```json
{"id":"C_PY_JSON","kind":"json","argv":["{python}","app.py","--case","small"],"expected":{"sum":5},"tracked_paths":["app.py"],"timeout_seconds":30}
```

## JavaScript와 TypeScript

Node.js가 설치된 프로젝트에서는 추가 패키지 없이 실제 함수 결과를 JSON으로 출력할 수 있습니다. 예를 들어 `src/sum.cjs`가 `sum` 함수를 내보내면 다음 검사가 `sum(2, 3)`의 결과를 비교합니다. `expected`의 `5`는 구현 출력에서 복사하지 말고 요구와 입력값에서 정합니다.

```json
{"id":"C_NODE","kind":"json","argv":["node","-e","const {sum}=require('./src/sum.cjs'); console.log(JSON.stringify({sum:sum(2,3)}));"],"expected":{"sum":5},"tracked_paths":["src/sum.cjs"],"timeout_seconds":10}
```

이 Node 예시는 공개 패키지 밖에서 만든 임시 합성 파일과 runner로 실행했습니다. 기대값이 `{"sum":5}`이면 통과했고, 의도적으로 `{"sum":6}`을 지정하면 출력 명령의 종료 코드가 0이어도 실패했습니다. 따라서 `json` 검사는 이 예시의 실제 반환값을 비교했습니다.

TypeScript 프로젝트에서는 **기존** 빌드 명령과 빌드한 JavaScript의 결과 검사를 연결합니다. 다음 항목은 **실행하지 않은 예시**입니다. 프로젝트에 `build` 스크립트가 있어야 하며, 빌드가 끝난 뒤 `dist/check-output.js`가 표준 출력에 JSON 하나를 써야 합니다. 실제 경로와 기대값은 프로젝트에 맞게 바꿉니다.

```json
[
  {"id":"C_BUILD","kind":"command","argv":["npm","run","build"],"tracked_paths":["package.json","package-lock.json","tsconfig.json","src"],"timeout_seconds":120},
  {"id":"C_TS_RESULT","kind":"json","argv":["node","dist/check-output.js"],"expected":{"sum":5},"tracked_paths":["src","dist/check-output.js","package.json","tsconfig.json"],"timeout_seconds":30}
]
```

프로젝트가 Vitest를 이미 설치했다면 로컬 실행 파일을 `command`로 호출할 수 있습니다. 다음 항목도 **실행하지 않은 예시**입니다. 패키지 설치나 네트워크 호출은 이 레시피에 포함되지 않습니다.

```json
{"id":"C_VITEST","kind":"command","argv":["./node_modules/.bin/vitest","run"],"tracked_paths":["src","tests","package.json","package-lock.json","vitest.config.ts"],"timeout_seconds":120}
```

`command`의 종료 코드 0은 프로세스 성공만 뜻합니다. Vitest 통과나 빌드 성공만으로 각 요구의 동작을 보장하지 않습니다. 동작 요구에는 독립적인 기대값을 둔 `json` 또는 정확한 `unittest` 검사를 연결합니다. `argv`는 셸 명령 문자열이 아니라 인수 배열입니다. 각 검사에 실제로 존재하는 입력, 코드와 설정을 `tracked_paths`로 지정합니다. `json` 명령은 표준 출력에 JSON 하나만 써야 합니다. 빌드 산출물을 검사에 사용한다면 생성 순서를 확인하고, 검사 도중 추적 파일이 바뀌지 않도록 합니다.
