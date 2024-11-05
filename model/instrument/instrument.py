from model.memory.market_data import MarketData
from model.position import Position




class Instrument:
    full_symbol: str
    def __init__(self, instrument_id, expired_date, exchange_id):
        self.id = instrument_id
        self.expired_date = expired_date
        self.expired_month = expired_date[:-2]
        self.exchange_id = exchange_id
        self.market_data: MarketData = MarketData()
        self.position = Position(instrument_id)

    def __str__(self) -> str:
        return (f"Instrument(id={self.id}, "
                f"expired_date={self.expired_date}, "
                f"expired_month={self.expired_month}, "
                f"exchange_id={self.exchange_id})")




