import re

def validate_future_id(instrument_id):
    pattern = r'^[A-Z]{2}\d{4}$'
    if not re.match(pattern, instrument_id, re.IGNORECASE):
        raise ValueError(f"期货代码格式无效：{instrument_id}")

class Instrument:
    id: str
    symbol: str
    bid = 0
    ask = 0
    bid_volume = 0
    ask_volume = 0
    available = False

    def __init__(self, instrument_id, expired_date):
        self.id = instrument_id
        self.expired_date = expired_date

class Future(Instrument):

    def __init__(self, instrument_id, expired_date):
        super().__init__(instrument_id, expired_date)
        # eg. IH2412
        validate_future_id(instrument_id)
        self.symbol = instrument_id