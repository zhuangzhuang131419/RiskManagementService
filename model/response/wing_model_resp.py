from model.memory.atm_volatility import ATMVolatility


class WingModelResp:
    def __init__(self, atm_volatility, k1, k2, b, atm_available):
        self.atm_volatility: float = atm_volatility
        self.k1: float = k1
        self.k2: float = k2
        self.b: float = b
        self.atm_available: bool = atm_available

    def to_dict(self):
        return {
            "atm_vol": self.atm_volatility,
            "k1": self.k1,
            "k2": self.k2,
            "b": self.b,
            "atm_available": self.atm_available
        }