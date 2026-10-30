# 합성 과제: 지연 주문 집계

이 자료는 하네스 사용성 검증을 위한 합성 과제입니다.

orders.csv를 읽어 고객별 지연 주문 건수를 JSON으로 출력하는 CLI를 만드세요.
고객 ID는 원본 문자열로 보존하며, 동일한 주문 ID는 처음 나타난 행만 사용합니다.
지연 시간은 minutes와 hours 단위를 지원하며 60분 이상이면 지연 주문입니다.
빈 고객 ID, 잘못된 숫자, 음수 지연 시간, 지원하지 않는 단위는 제외하고 excluded_rows에 건수를 기록합니다.
중복 주문으로 제외한 행은 duplicate_rows에 기록하며 excluded_rows와 중복 집계하지 않습니다.
JSON은 counts, excluded_rows, duplicate_rows 세 필드를 포함합니다. counts는 지연 주문이 있는 고객만 고객 ID 문자열 순으로 정렬합니다.

제출 파일은 solution.py, tests 디렉터리, README.md입니다.
