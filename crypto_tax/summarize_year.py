import datetime
import decimal

from crypto_tax import db
from crypto_tax import models


def get_rate(currency, date):
    rate = db.session.query(models.FiatExchangeRate)\
        .filter(models.FiatExchangeRate.currency == currency)\
        .filter(models.FiatExchangeRate.authority_currency == 'PLN')\
        .filter(models.FiatExchangeRate.authority == 'NBP')\
        .filter(models.FiatExchangeRate.valid_date <= date)\
        .order_by(models.FiatExchangeRate.valid_date.desc())\
        .first()
    if rate is None:
        print(f'No rate for {date}')
    if rate.valid_date != date:
        print(f'Used {rate.valid_date} in place of missing {date}')
    return rate


def print_table(year):
    start_date = datetime.datetime(year=year, month=1, day=1)
    end_date = datetime.datetime(year=year+1, month=1, day=1)
    sum_value = decimal.Decimal(0)
    sum_fee = decimal.Decimal(0)
    # No join in sqlite
    query = db.session.query(models.FiatCryptoOperation)\
        .filter(models.FiatCryptoOperation.performed_at >= start_date)\
        .filter(models.FiatCryptoOperation.performed_at < end_date)\
        .order_by(models.FiatCryptoOperation.performed_at)
    for operation in query:
        rate = get_rate(operation.fiat_currency, operation.performed_at.date())
        local_value = decimal.Decimal(operation.value) * rate.absolute_rate()
        sum_value += local_value
        local_fee = decimal.Decimal(operation.fee) * rate.absolute_rate()
        sum_fee += local_fee
        print(f"{operation.performed_at} {local_value} {local_fee}")
    print('='*10)
    tax = (sum_value - sum_fee) * decimal.Decimal('0.19')
    print(f"total: {sum_value} - {sum_fee} = {sum_value-sum_fee}; tax = {tax}")


def vesting_costs(year):
    quarters = [
        datetime.date(year, 3, 31),
        datetime.date(year, 6, 30),
        datetime.date(year, 9, 30),
        datetime.date(year, 12, 31),
    ]
    value_usd = decimal.Decimal(input('Single vesting value in USD: '))
    total_pln = decimal.Decimal(0)
    for q in quarters:
        rate = get_rate('USD', q)
        value_pln = value_usd * rate.absolute_rate()
        total_pln += value_pln
        print(f'{q} - {value_usd} * {rate.absolute_rate()} = {value_pln}')
    print(f"total vesting value (cost) = {total_pln}")


if __name__ == '__main__':
    import sys
    year = int(sys.argv[1])
    print_table(year)
    vesting_costs(year)
