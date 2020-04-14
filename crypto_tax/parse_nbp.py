#/usr/bin/env python3

import csv
import datetime
import decimal
import itertools

from crypto_tax import db
from crypto_tax import models


def import_path(p):
    state = 'header'
    data = []
    currency_names = []
    amounts = []
    with open(p, newline='', encoding='cp1250') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            assert not row or row[-1] == ''
            if state == 'header':
                state = 'second_header'
                continue
            if state == 'second_header':
                state = 'data'
                continue
            if state == 'data':
                if not row:
                    state = 'footer'
                    continue
                data.append(row[:-3])
                continue
            if state == 'footer':
                assert row[0] == 'kod ISO'
                currency_names.extend(row[1:-1])
                state = 'footer_names'
                continue
            if state == 'footer_names':
                assert row[0] == 'nazwa waluty'
                state = 'footer_amounts'
                continue
            if state == 'footer_amounts':
                assert row[0] == 'liczba jednostek'
                amounts.extend(row[1:-1])
                state = 'finished'
                continue
            if state == 'finished':
                print(f'extra row: {row}')
    print(f'state {state} data: {len(data)} currencies: {currency_names}')
    mapped = {}
    for key, value in itertools.zip_longest(currency_names, amounts):
        mapped[key] = {'amount': int(value)}
    for entry in data:
        date = datetime.datetime.strptime(entry[0], '%Y%m%d').date()
        for currency, value in itertools.zip_longest(currency_names, entry[1:]):
            model = models.FiatExchangeRate(
                authority='NBP',
                authority_currency='PLN',
                currency=currency,
                amount=mapped[currency]['amount'],
                valid_date=date,
                exchange_rate = str(decimal.Decimal(value.replace(',', '.'))),
            )
            db.session.add(model)
    db.session.commit()

if __name__ == '__main__':
    import sys
    import_path(sys.argv[1])
