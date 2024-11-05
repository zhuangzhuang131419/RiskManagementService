import re
from model.instrument.instrument import Instrument

def validate_future_id(instrument_id):
    pattern = r'^[A-Z]{2}\d{4}$'
    if not re.match(pattern, instrument_id, re.IGNORECASE):
        return False
    return True

class Future(Instrument):

    def __init__(self, instrument_id: str, expired_date: str, exchange_id: str, underlying_id: str):
        # eg. IH2412
        super().__init__(instrument_id, expired_date, exchange_id)
        if validate_future_id(instrument_id):
            self.symbol = underlying_id + expired_date
            self.full_symbol = self.symbol
        else:
            raise ValueError(f"期货代码格式无效：{instrument_id}")