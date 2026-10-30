import csv
import json
from pathlib import Path


def summarize(rows, minimum=3):
    totals = {}
    for row in rows:
        product = row['product_id']
        raw_quantity = row['quantity']
        if not product or not raw_quantity.isdigit():
            raise ValueError('ID and a nonnegative integer quantity are required')
        totals[product] = totals.get(product, 0) + int(raw_quantity)
    return {key: totals[key] for key in sorted(totals) if totals[key] >= minimum}


if __name__ == '__main__':
    with Path('orders.csv').open(newline='') as stream:
        print(json.dumps(summarize(csv.DictReader(stream))))
