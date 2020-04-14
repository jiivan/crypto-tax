import csv
import datetime
import decimal

from crypto_tax import db
from crypto_tax import models


def split_currency_amount(s):
    amount_str, currency = s.split(' ', 1)
    amount = decimal.Decimal(amount_str)
    return amount, currency


def import_path(p):
    with open(p, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ['Type', 'Datetime', 'Account', 'Amount', 'Value', 'Rate', 'Fee', 'Sub Type', ]
        for row in reader:
            assert row[0] == "Market"
            assert row[2] == 'Main Account'
            dt = datetime.datetime.strptime(row[1], '%b. %d, %Y, %I:%M %p')
            amount, crypto_currency = split_currency_amount(row[3])
            value, fiat_currency = split_currency_amount(row[4])
            rate, rate_currency = split_currency_amount(row[5])
            assert rate_currency == fiat_currency
            fee, fee_currency = split_currency_amount(row[6])
            assert fee_currency == fiat_currency
            sub_type = row[7]
            assert sub_type in ("Sell", "Buy", )
            if sub_type == 'Sell':
                amount *= -1
            model = models.FiatCryptoOperation(
                exchange_name='Bitstamp',
                crypto_currency=crypto_currency,
                fiat_currency=fiat_currency,
                amount=str(amount),
                value=str(value),
                fee=str(fee),
                performed_at=dt,
            )
            #print(f"{model.rate()} {rate}")
            #assert model.rate() == rate
            db.session.add(model)
            print(model)
    db.session.commit()


if __name__ == '__main__':
    import sys
    import_path(sys.argv[1])
