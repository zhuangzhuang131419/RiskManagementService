class Instrument:
    id: str

    def __init__(self, instrument_id):
        self.id = instrument_id

class Future(Instrument):

    def __init__(self, instrument_id):
        super().__init__(instrument_id)
        # eg. IH2412
        self.symbol = self.id[:2]
        self.bid = float
        self.ask = float
        self.bid_volume = float
        self.ask_volume = float
        self.available = True