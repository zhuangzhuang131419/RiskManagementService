from model.response.option_resp_base import OptionRespBase


class OptionGreeksResp(OptionRespBase):
    pass


class OptionGreeksData:
    def __init__(self, delta, gamma, vega, theta, vanna_vs, vanna_sv, db, dkurt, position, ask, bid):
        self.delta = round(delta, 2)
        self.gamma = round(gamma, 2)
        self.vega = round(vega, 2)
        self.theta = round(theta, 2)
        self.vanna_vs = round(vanna_vs, 2)
        self.vanna_sv = round(vanna_sv, 2)
        self.db = round(db, 2)
        self.dkurt = round(dkurt, 2)
        self.position = position
        self.ask = round(ask, 2)
        self.bid = round(bid, 2)

    def to_dict(self):
        return {
            "delta": self.delta,
            "gamma": self.gamma,
            "vega": self.vega,
            "theta": self.theta,
            "vanna_vs": self.vanna_vs,
            "vanna_sv": self.vanna_vs,
            "dkurt": self.dkurt,
            "db": self.db,
            "position": self.position,
            "ask": self.ask,
            "bid": self.bid
        }

