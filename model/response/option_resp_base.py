from typing import Dict

class OptionRespBase:
    def __init__(self, symbol):
        self.symbol = symbol
        self.strike_prices: Dict[float, StrikePrices] = {}

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "strike_prices": {sp: self.strike_prices[sp].to_dict() for sp in self.strike_prices}
        }

class StrikePrices:
    def __init__(self, call_option, put_option):
        self.call_option = call_option
        self.put_option = put_option

    def to_dict(self):
        return {
            "call_option": self.call_option.to_dict(),
            "put_option": self.put_option.to_dict()
        }