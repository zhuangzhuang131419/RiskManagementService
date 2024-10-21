from model.response.option_resp_base import OptionRespBase


class OptionGreeksResp(OptionRespBase):
    pass


class OptionGreeksData:
    def __init__(self, delta, gamma, vega, theta):
        self.delta = round(delta, 2)
        self.gamma = round(gamma, 2)
        self.vega = round(vega, 2)
        self.theta = round(theta, 2)

    def to_dict(self):
        return {
            "delta": self.delta,
            "gamma": self.gamma,
            "vega": self.vega,
            "theta": self.theta
        }

