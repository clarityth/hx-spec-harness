"""Count delayed orders per customer from a CSV file."""

import argparse
import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


def summarize(path: Path) -> dict:
    counts: dict[str, int] = {}
    seen_orders: set[str] = set()
    excluded_rows = 0
    duplicate_rows = 0

    with path.open("r", encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            order_id = row.get("order_id")
            if order_id in seen_orders:
                duplicate_rows += 1
                continue
            seen_orders.add(order_id)

            customer_id = row.get("customer_id")
            unit = row.get("unit")
            raw_delay = row.get("delay")
            try:
                delay = Decimal(raw_delay) if raw_delay is not None else None
            except InvalidOperation:
                delay = None

            if (
                not customer_id
                or delay is None
                or not delay.is_finite()
                or delay < 0
                or unit not in {"minutes", "hours"}
            ):
                excluded_rows += 1
                continue

            minutes = delay * (60 if unit == "hours" else 1)
            if minutes >= 60:
                counts[customer_id] = counts.get(customer_id, 0) + 1

    return {
        "counts": dict(sorted(counts.items())),
        "excluded_rows": excluded_rows,
        "duplicate_rows": duplicate_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "csv_path", nargs="?", type=Path, default=Path(__file__).with_name("orders.csv")
    )
    args = parser.parse_args()
    print(json.dumps(summarize(args.csv_path), ensure_ascii=False))


if __name__ == "__main__":
    main()
