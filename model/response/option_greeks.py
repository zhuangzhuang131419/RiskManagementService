from model.response.option_resp_base import OptionRespBase


class OptionGreeksResp(OptionRespBase):
    pass


class OptionGreeksData:
    def __init__(self, delta, gamma, vega, theta, vanna_vs, vanna_sv, db, dkurt, position, ask, bid):
        self.delta = delta
        self.gamma = gamma
        self.vega = vega
        self.theta = theta
        self.vanna_vs = vanna_vs
        self.vanna_sv = vanna_sv
        self.db = db
        self.dkurt = dkurt
        self.position = position
        self.ask = ask
        self.bid = bid

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

