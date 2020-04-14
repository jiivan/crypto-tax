# Use String instead of DECIMAL, because sqlite doesn't support decimals
import decimal
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext import declarative
from sqlalchemy.sql import func


Base = declarative.declarative_base()


class TimestampedMixin():
    @declarative.declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    modified_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

class FiatExchangeRate(TimestampedMixin, Base):
    authority = Column(String, nullable=False)
    authority_currency = Column(String(3), nullable=False)
    currency = Column(String(3), nullable=False)
    amount = Column(Integer, nullable=False)  # liczba jednostek 1 lub 100
    valid_date = Column(Date, nullable=False)
    exchange_rate = Column(String, nullable=False)

    def absolute_rate(self):
        return (decimal.Decimal(self.exchange_rate) / decimal.Decimal(self.amount)).quantize(decimal.Decimal('1.00'))

    __table_args__ = (
        UniqueConstraint(
            'authority',
            'authority_currency',
            'currency',
            'valid_date',
        ),
    )


class FiatCryptoOperation(TimestampedMixin, Base):
    exchange_name = Column(String, nullable=False)
    crypto_currency = Column(String(3), nullable=False)
    fiat_currency = Column(String(3), nullable=False)
    amount = Column(String, nullable=False)  # Amount of crypto assets. + = BUY - = SELL
    value = Column(String, nullable=False)  # Amount of fiat assets
    fee = Column(String, nullable=False)  # Fee in fiat currency
    performed_at = Column(DateTime, nullable=False)

    def rate(self):
        return (decimal.Decimal(self.value) / abs(decimal.Decimal(self.amount))).quantize(
            decimal.Decimal('1.00'),
            decimal.ROUND_HALF_UP,
        )

    def __str__(self):
        return f"{self.performed_at}, {self.amount} {self.crypto_currency}, {self.value} {self.fiat_currency}, {self.fee} {self.fiat_currency}"


# Base.metadata.create_all(engine)
