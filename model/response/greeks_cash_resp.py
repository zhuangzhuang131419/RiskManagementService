
class GreeksCashResp:
    delta: float
    delta_cash: float
    gamma_p_cash: float
    vega_cash: float
    db_cash: float
    vanna_vs_cash: float
    vanna_sv_cash: float
    charm_cash: float
    dkurt_cash: float

    def __init__(self, delta: float, delta_cash: float, gamma_p_cash: float, vega_cash: float,
                 db_cash: float, vanna_vs_cash: float, vanna_sv_cash: float, charm_cash: float, dkurt_cash: float):
        """
        Initializes a GreeksCashResp object with the given values.
        """
        self.delta = delta
        self.delta_cash = delta_cash
        self.gamma_p_cash = gamma_p_cash
        self.vega_cash = vega_cash
        self.db_cash = db_cash
        self.vanna_vs_cash = vanna_vs_cash
        self.vanna_sv_cash = vanna_sv_cash
        self.charm_cash = charm_cash
        self.dkurt_cash = dkurt_cash

    def to_dict(self) -> dict:
        """
        Converts the instance to a dictionary.

        :return: A dictionary representation of the instance
        """
        return {
            "delta": self.delta,
            "delta_cash": self.delta_cash,
            "gamma_p_cash": self.gamma_p_cash,
            "vega_cash": self.vega_cash,
            "db_cash": self.db_cash,
            "vanna_vs_cash": self.vanna_vs_cash,
            "vanna_sv_cash": self.vanna_sv_cash,
            "charm_cash": self.charm_cash
        }