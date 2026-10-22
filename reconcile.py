#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from decimal import Decimal

# txn_id -> ((ts, line_number), event); only the latest attempt is kept.
latest = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line_no, line in enumerate(f):
        try:
            event = json.loads(line)
        except ValueError:
            continue  # unreadable (truncated) line
        if not isinstance(event, dict):
            continue
        txn_id = event.get("txn_id")
        if txn_id is None or str(txn_id).strip() == "":
            continue  # no txn_id
        key = (event["ts"], line_no)  # ts is uniform ISO-8601 UTC, so it sorts as text
        if txn_id not in latest or key > latest[txn_id][0]:
            latest[txn_id] = (key, event)


def parse_amount(value):
    # Amounts arrive as numbers or as strings such as "4,804.15".
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    return Decimal(str(value))


total = Decimal(0)
count = 0
for _, event in latest.values():
    if event["status"] == "success":
        total += parse_amount(event["amount"])
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
