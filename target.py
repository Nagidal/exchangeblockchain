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
    transaction_type: Optional[str] = field(init=False)
    from_quantity: Optional[float] = field(init=False)
    from_currency: Optional[str] = field(init=False)
    to_quantity: Optional[float] = field(init=False)
    to_currency: Optional[str] = field(init=False)
    fees_paid: Optional[float] = field(init=False)
    fees_currency: Optional[str] = field(init=False)
    timestamp: Optional[str] = field(init=False)
    acquisition_timestamp: Optional[str] = field(init=False)
    note: Optional[str] = field(init=False)
    source_row: InitVar[source.Rows]
    def __post_init__(self, source_row):
        self.from_quantity = None
        self.from_currency = None
        self.to_quantity = None
        self.to_currency = None
        self.fees_paid = None
        self.fees_currency = None
        self.timestamp = None
        self.acquisition_timestamp = None
        self.note = None
        if type(source_row) is source.Deposit:
            self.transaction_type = "Deposit"
            self.to_quantity = float(source_row.amount[1:].replace(",", "_"))
            self.to_currency = source_row.currency
            self.fees_paid = 0
            self.fees_currency = self.to_currency
            with setlocale('C'):
                self.timestamp = datetime.strptime(
                        source_row.date_time, settings.bce_time_format
                        ).replace(tzinfo=timezone.utc)
        elif type(source_row) is source.Withdrawal:
            self.transaction_type = "Withdrawal"
            self.from_quantity = source_row.amount
            self.from_currency = source_row.currency
            self.fees_paid = 0
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
                    self.to_quantity = float(source_row.quantity_transacted)
                    self.from_currency = source_row.counter_asset
                    self.from_quantity = float(source_row.counter_amount)
                elif source_row.transaction_type == "SELL":
                    self.to_currency = source_row.counter_asset
                    self.to_quantity = float(source_row.counter_amount)
                    self.from_currency = source_row.asset
                    self.from_quantity = float(source_row.quantity_transacted)
                self.fees_paid = float(source_row.fee_amount)
                self.fees_currency = source_row.fee_asset
                self.note = f"Order_ID: {source_row.order_id}, Transaction_ID: {source_row.transaction_id}"
