from model.response.option_resp_base import OptionRespBase


class OptionMarketResp(OptionRespBase):
    pass

class OptionData:
    def __init__(self, bid_price, bid_volume, ask_price, ask_volume):
        self.bid_price = bid_price
        self.bid_volume = bid_volume
        self.ask_price = ask_price
        self.ask_volume = ask_volume

    def to_dict(self):
        return {
            "bid_price": self.bid_price,
            "ask_price": self.ask_price,
            "bid_volume": self.bid_volume,
            "ask_volume": self.ask_volume
        }