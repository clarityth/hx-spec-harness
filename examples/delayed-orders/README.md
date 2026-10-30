# 지연 주문 집계

Python 3.11 이상에서 표준 라이브러리만 사용합니다. 다음 명령은 같은 폴더의 `orders.csv`를 읽고 JSON 한 개를 표준 출력에 씁니다.

```sh
python3 solution.py
```

다른 입력 파일을 읽을 때는 경로를 지정합니다.

```sh
python3 solution.py /path/to/orders.csv
```

중복 주문은 파일에 먼저 나온 행을 사용합니다. 그 행이 유효하지 않아도 같은 주문 ID의 뒤쪽 행은 중복으로 집계합니다. 지연 시간은 유한한 0 이상의 십진수로 해석합니다. 고객 ID는 원본 문자열을 유지합니다.

하네스로 검사할 때는 과제 원문과 계약을 확인하고 계획을 먼저 제시합니다. 다음 명령의 승인 문구와 근거 위치에는 **사용자가 실제로 남긴 답변**만 적습니다. 합성 예제에 계획 파일이 있어도 사용자 승인 기록이 자동으로 생기지는 않습니다.

```sh
python3 <toolkit>/hx.py --root . install
python3 .harness-kit/hx.py --root . init
cp contract.example.json .harness/contract.json
cp plan.example.json .harness/plan.json
python3 .harness-kit/hx.py --root . plan
python3 .harness-kit/hx.py --root . plan-approve --actor user --quote '<실제 승인 문구>' --source '<답변 위치>'
python3 -m unittest discover -s tests -v
python3 .harness-kit/hx.py --root . check
python3 .harness-kit/hx.py --root . status
python3 .harness-kit/hx.py --root . freeze
```

제공된 입력의 기대 결과는 `{"counts": {"001": 2, "1": 1}, "excluded_rows": 4, "duplicate_rows": 1}`입니다. `freeze`는 현재 파일과 검사 근거를 확인합니다. 실제 제출 완료를 뜻하지 않습니다.
