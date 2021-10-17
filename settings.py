#!/usr/bin/env python


from pathlib import Path


transactions_source = Path("2020.csv")
deposits_source = Path("deposits.tsv")
withdrawals_source = Path("withdrawals.tsv")
transactions_columns = "date_time_utc,transaction_type,asset,quantity_transacted,counter_asset,counter_amount,price,fee_asset,fee_amount,order_id,transaction_id".split(",")
deposits_columns = "currency	amount	date_time	status	confirmations	transaction_hash".split("\t")
withdrawals_columns = deposits_columns


bce_time_format = "%m/%d/%Y, %I:%M:%S %p"
bce_transaction_time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
