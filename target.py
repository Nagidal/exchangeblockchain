#!/usr/bin/env python


import threading
import locale
from contextlib import contextmanager
from dataclasses import dataclass
from dataclasses import field
from dataclasses import InitVar
from datetime import datetime
from datetime import timezone
from typing import Optional
from typing import Mapping
import source
import settings


# from https://stackoverflow.com/a/24070673
LOCALE_LOCK = threading.Lock()
@contextmanager
def setlocale(name):
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)


@dataclass
class Row:
    transaction_type: str = field(init=False)
    from_quantity: str = field(init=False)
    from_currency: str = field(init=False)
    to_quantity: str = field(init=False)
    to_currency: str = field(init=False)
    fees_paid: str = field(init=False)
    fees_currency: str = field(init=False)
    timestamp: str = field(init=False)
    acquisition_timestamp: str = field(init=False)
    note: str = field(init=False)
    source_row: InitVar[source.Rows]
    def __post_init__(self, source_row):
        self.from_quantity = ""
        self.from_currency = ""
        self.to_quantity = ""
        self.to_currency = ""
        self.fees_paid = "0"
        self.fees_currency = ""
        self.timestamp = ""
        self.acquisition_timestamp = ""
        self.note = ""
        if type(source_row) is source.Deposit:
            self.transaction_type = "Deposit"
            self.to_quantity = source_row.amount[1:].replace(",", "")
            self.to_currency = source_row.currency
            self.fees_currency = self.to_currency
            with setlocale('C'):
                self.timestamp = datetime.strptime(
                        source_row.date_time, settings.bce_time_format
                        ).replace(tzinfo=timezone.utc)
        elif type(source_row) is source.Withdrawal:
            self.transaction_type = "Withdrawal"
            self.from_quantity = source_row.amount
            self.from_currency = source_row.currency
            self.fees_currency = self.from_currency
            with setlocale('C'):
                self.timestamp = datetime.strptime(
                        source_row.date_time, settings.bce_time_format
                        ).replace(tzinfo=timezone.utc)
            self.note = f"transaction hash: {source_row.transaction_hash}"
        elif type(source_row) is source.Transaction:
            self.transaction_type = "Trade"
            with setlocale('C'):
                self.timestamp = datetime.strptime(
                        source_row.date_time_utc, settings.bce_transaction_time_format
                        ).replace(tzinfo=timezone.utc)
                if source_row.transaction_type == "BUY":
                    self.to_currency = source_row.asset
                    self.to_quantity = source_row.quantity_transacted
                    self.from_currency = source_row.counter_asset
                    self.from_quantity = source_row.counter_amount
                elif source_row.transaction_type == "SELL":
                    self.to_currency = source_row.counter_asset
                    self.to_quantity = source_row.counter_amount
                    self.from_currency = source_row.asset
                    self.from_quantity = source_row.quantity_transacted
                self.fees_paid = source_row.fee_amount
                self.fees_currency = source_row.fee_asset
                self.note = f"order_id: {source_row.order_id}, transaction_id: {source_row.transaction_id}"
    def as_dict(self) -> Mapping[str, str]:
        if self.timestamp.hour < 10:
            timestring = "".join((
                datetime.strftime(self.timestamp, settings.target_time_format[:9]),
                f"{self.timestamp.hour}",
                datetime.strftime(self.timestamp, settings.target_time_format[11:]),
                ))
        else:
            timestring = datetime.strftime(self.timestamp, settings.target_time_format)
        return dict((
            ("Transaction Type", f"{self.transaction_type}"),
            ("From quantity", f"{self.from_quantity}"),
            ("From currency", f"{self.from_currency}"),
            ("To quantity", f"{self.to_quantity}"),
            ("To currency", f"{self.to_currency}"),
            ("Fees paid", f"{self.fees_paid}"),
            ("Fee currency", f"{self.fees_currency}"),
            ("Timestamp", f"{timestring}"),
            ("Acquisition Timestamp", f""),
            ("Note", f"{self.note}"),
            ))
