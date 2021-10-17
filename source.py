#!/usr/bin/env python


import settings
import csv
from pathlib import Path
from dataclasses import dataclass
from dataclasses import make_dataclass
from dataclasses import field
from dataclasses import InitVar
from typing import Mapping
from typing import Union
from typing import Iterable


def post_init(self, _dict):
    for k, v in _dict.items():
        setattr(self, k, v)


Transaction, Deposit, Withdrawal = (
        make_dataclass(
            name,
            [(fld, str, field(init=False)) for fld in cols] + [("_dict", InitVar[Mapping[str, str]], None)],
            namespace={
                "__post_init__": post_init
                },
            )
        for name, cols, in (
            ("Transaction", settings.transactions_columns),
            ("Deposit", settings.deposits_columns),
            ("Withdrawal", settings.withdrawals_columns),
            )
    )


Rows = Union[Deposit, Transaction, Withdrawal]


def read_csv(source: Path, dialect: Mapping[str, str], Row: Rows) -> Iterable[Rows]:
    with open(source, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, **dialect)
        for row in reader:
            r = Row(row)
            yield r


def read_sources() -> Iterable[Rows]:
    for path, dialect, Row in (
            (settings.deposits_source, {"delimiter": "\t"}, Deposit),
            (settings.transactions_source, {}, Transaction),
            (settings.withdrawals_source, {"delimiter": "\t"}, Withdrawal),
            ):
        yield from read_csv(path, dialect, Row)
