"""
Generate synthetic seed data for the monetizing dashboard dbt project.

Fixed random seed -> reproducible output. Run once:
    python scripts/generate_seeds.py

Writes:
    seeds/raw_contacts.csv   (~25k rows)
    seeds/raw_channels.csv   (5 rows)
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

ROOT = Path(__file__).resolve().parent.parent
SEEDS = ROOT / "seeds"
SEEDS.mkdir(exist_ok=True)

# --- dimensions -------------------------------------------------------------

CHANNELS = ["SMS", "Email", "App-push", "Stories", "Banner"]
CHANNEL_GROUPS = {
    "SMS": "Direct",
    "Email": "Direct",
    "App-push": "Direct",
    "Stories": "Display",
    "Banner": "Display",
}

PRODUCTS = [
    "Carsharing",
    "Debit card",
    "Credit card",
    "Videoplatform",
    "Browser",
]

DEVICES = ["Phone", "Tablet", "Desktop"]

START_DATE = date(2026, 7, 1)
END_DATE = date(2026, 9, 30)

TARGET_ROWS = 25_000
USER_POOL = 1_000
DUPLICATE_RATE = 0.07  # ~7% duplicate on (date, channel, product, device, contact_id)


# --- channels seed ----------------------------------------------------------

def write_channels():
    path = SEEDS / "raw_channels.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["contact_channel", "channel_group"])
        for ch in CHANNELS:
            writer.writerow([ch, CHANNEL_GROUPS[ch]])
    print(f"wrote {path} ({len(CHANNELS)} rows)")


# --- contacts seed ----------------------------------------------------------

def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def write_contacts():
    days = list(daterange(START_DATE, END_DATE))
    combos = [
        (ch, prod, dev)
        for ch in CHANNELS
        for prod in PRODUCTS
        for dev in DEVICES
    ]
    user_pool = list(range(1, USER_POOL + 1))

    unique_target = int(TARGET_ROWS * (1 - DUPLICATE_RATE))
    dup_target = TARGET_ROWS - unique_target

    seen = set()
    rows = []

    while len(rows) < unique_target:
        d = random.choice(days)
        ch, prod, dev = random.choice(combos)
        uid = random.choice(user_pool)
        key = (d, ch, prod, dev, uid)
        if key in seen:
            continue
        seen.add(key)
        rows.append({
            "contact_date": d,
            "contact_channel": ch,
            "product_promoted": prod,
            "device_type_name": dev,
            "contact_id": uid,
        })

    for _ in range(dup_target):
        src = random.choice(rows[:unique_target])
        rows.append(dict(src))

    random.shuffle(rows)

    path = SEEDS / "raw_contacts.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "contact_id",
            "contact_date",
            "contact_channel",
            "product_promoted",
            "device_type_name",
            "contact_count",
        ])
        for row in rows:
            contact_count = random.randint(1, 50)
            writer.writerow([
                row["contact_id"],
                row["contact_date"].isoformat(),
                row["contact_channel"],
                row["product_promoted"],
                row["device_type_name"],
                contact_count,
            ])
    print(f"wrote {path} ({len(rows)} rows, {dup_target} duplicates on grain)")


if __name__ == "__main__":
    write_channels()
    write_contacts()