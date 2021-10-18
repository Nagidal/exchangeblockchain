#!/usr/bin/env python


from loguru import logger
import source
import target
import settings
import csv
from pathlib import Path
from io import TextIOWrapper
from contextlib import contextmanager


@contextmanager
def write_headers(path: Path) -> TextIOWrapper:
    with open(path, mode="w", encoding="utf-8") as fd:
        print("Blockpit Excel Template;;;;;;;;;Version: 1.1", file=fd)
        print("*keep row 1-3 unchanged!;;;;;;;;;", file=fd)
        yield fd


def sort_transactions() -> list[target.Row]:
    transactions = [target.Row(r) for r in source.read_sources()]
    transactions.sort(key=lambda r: r.timestamp)
    return transactions


if __name__ == "__main__":
    with write_headers(settings.target_file) as fd:
        writer = csv.DictWriter(fd, fieldnames=settings.target_columns, delimiter=";")
        writer.writeheader()
        for t in sort_transactions():
            logger.debug(t.as_dict())
            writer.writerow(t.as_dict())
