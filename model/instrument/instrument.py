import re

from model.memory.market_data import MarketData


def validate_future_id(instrument_id):
    pattern = r'^[A-Z]{2}\d{4}$'
    if not re.match(pattern, instrument_id, re.IGNORECASE):
        return False
    return True

class Instrument:
    id: str
    symbol: str

    def __init__(self, instrument_id, expired_date):
        self.id = instrument_id
        self.expired_date = expired_date
        self.market_data = MarketData()

class Future(Instrument):

    def __init__(self, instrument_id, expired_date):
        super().__init__(instrument_id, expired_date)
        # eg. IH2412
        if validate_future_id(instrument_id):
            self.symbol = instrument_id
        else:
            raise ValueError(f"期货代码格式无效：{instrument_id}")
