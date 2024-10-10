class Instrument:
    id: str
    name: str
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
        self.name = self.id[:2]