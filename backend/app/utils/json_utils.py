from decimal import Decimal


def to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value
