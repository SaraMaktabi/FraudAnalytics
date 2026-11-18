"""Prepare a reduced transaction dataset for local EDA.

The script never modifies source files. It uses pandas chunks for transactions
and a disk-backed SQLite index while filtering the large labels JSON file.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

import pandas as pd


CHUNK_SIZE = 100_000
START_DATE = pd.Timestamp("2015-01-01")
LABEL_PATTERN = re.compile(rb'"(\d+)"\s*:\s*"(Yes|No)"')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transactions", type=Path, default=None)
    parser.add_argument(
        "--labels", type=Path, default=Path("data/raw/train_fraud_labels.json")
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("data/prepared")
    )
    return parser.parse_args()


def default_transactions_path() -> Path:
    for candidate in (Path("data/raw/transactions.csv"), Path("data/raw/transactions_data.csv")):
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Aucun fichier transactions.csv ou transactions_data.csv trouvé.")


def create_id_index(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE retained_ids (transaction_id TEXT PRIMARY KEY)")
    return connection


def prepare_transactions(source: Path, output: Path, index: sqlite3.Connection) -> dict:
    if not source.exists():
        raise FileNotFoundError(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    stats = {
        "initial": 0,
        "retained": 0,
        "batch": 0,
        "streaming": 0,
        "min_date": None,
        "max_date": None,
    }
    first_output = True
    for chunk in pd.read_csv(source, chunksize=CHUNK_SIZE, dtype={"id": "string"}):
        if "date" not in chunk.columns or "id" not in chunk.columns:
            raise ValueError("Le fichier transactions doit contenir les colonnes 'id' et 'date'.")
        stats["initial"] += len(chunk)
        dates = pd.to_datetime(chunk["date"], errors="coerce")
        selected = chunk.loc[dates >= START_DATE].copy()
        selected_dates = dates.loc[selected.index]
        if selected.empty:
            continue

        selected.to_csv(output, mode="w" if first_output else "a", index=False, header=first_output)
        first_output = False
        ids = [(str(value),) for value in selected["id"].dropna()]
        index.executemany("INSERT OR IGNORE INTO retained_ids VALUES (?)", ids)
        index.commit()
        stats["retained"] += len(selected)
        stats["batch"] += int(((selected_dates.dt.year >= 2015) & (selected_dates.dt.year <= 2018)).sum())
        stats["streaming"] += int((selected_dates.dt.year == 2019).sum())
        current_min, current_max = selected_dates.min(), selected_dates.max()
        stats["min_date"] = current_min if stats["min_date"] is None else min(stats["min_date"], current_min)
        stats["max_date"] = current_max if stats["max_date"] is None else max(stats["max_date"], current_max)
    return stats


def prepare_labels(source: Path, output: Path, index: sqlite3.Connection) -> Counter:
    if not source.exists():
        raise FileNotFoundError(source)
    counts: Counter = Counter()
    output.unlink(missing_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    first = True
    carry = b""
    with source.open("rb") as input_file, output.open("wb") as output_file:
        output_file.write(b'{"target": {')
        for block in iter(lambda: input_file.read(4 * 1024 * 1024), b""):
            data = carry + block
            previous_carry_length = len(carry)
            matches = list(LABEL_PATTERN.finditer(data))
            if block:
                carry = data[max(0, len(data) - 128) :]
            for match in matches:
                if match.end() <= previous_carry_length:
                    continue
                transaction_id = match.group(1).decode("ascii")
                label = match.group(2).decode("ascii")
                exists = index.execute(
                    "SELECT 1 FROM retained_ids WHERE transaction_id = ?", (transaction_id,)
                ).fetchone()
                if exists:
                    if not first:
                        output_file.write(b", ")
                    output_file.write(json.dumps(transaction_id).encode() + b": " + json.dumps(label).encode())
                    first = False
                    counts[label] += 1
        output_file.write(b"}}\n")
    return counts


def format_size(path: Path) -> str:
    return f"{path.stat().st_size / (1024 * 1024):,.2f} MiB"


def main() -> None:
    args = parse_args()
    transactions = args.transactions or default_transactions_path()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / ".retained_ids.sqlite"
    index_path.unlink(missing_ok=True)
    index = create_id_index(index_path)
    try:
        stats = prepare_transactions(transactions, output_dir / "transactions.csv", index)
        label_counts = prepare_labels(args.labels, output_dir / "train_fraud_labels.json", index)
    finally:
        index.close()
        index_path.unlink(missing_ok=True)

    final_transactions = output_dir / "transactions.csv"
    reduction = 100 * (1 - stats["retained"] / stats["initial"]) if stats["initial"] else 0
    print(f"Nombre initial de transactions : {stats['initial']:,}")
    print(f"Nombre de transactions retenues : {stats['retained']:,}")
    print(f"Pourcentage de réduction : {reduction:.2f} %")
    print(f"Taille initiale : {format_size(transactions)}")
    print(f"Taille finale : {format_size(final_transactions)}")
    print(f"Période temporelle retenue : {stats['min_date']} à {stats['max_date']}")
    print(f"Nombre de transactions labellisées : {sum(label_counts.values()):,}")
    print(f"Répartition des labels : Yes={label_counts['Yes']:,}, No={label_counts['No']:,}")
    print(f"Transactions 2015-2018 destinées au batch : {stats['batch']:,}")
    print(f"Transactions 2019 destinées au streaming : {stats['streaming']:,}")


if __name__ == "__main__":
    main()
