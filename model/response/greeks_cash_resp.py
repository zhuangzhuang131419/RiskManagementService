
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

    def __init__(self, investor_id: str = None, delta: float = 0.0, delta_cash: float = 0.0, gamma_p_cash: float = 0.0, vega_cash: float = 0, theta_cash: float = 0,
                 db_cash: float = 0.0, vanna_vs_cash: float = 0.0, vanna_sv_cash: float = 0.0, charm_cash: float = 0.0, dkurt_cash: float = 0.0, underlying_price: float = 0.0):
        """
        Initializes a GreeksCashResp object with the given values.
        """
        self.delta = delta
        self.investor_id = investor_id
        self.delta_cash = delta_cash
        self.gamma_p_cash = gamma_p_cash
        self.vega_cash = vega_cash
        self.theta_cash = theta_cash
        self.db_cash = db_cash
        self.vanna_vs_cash = vanna_vs_cash
        self.vanna_sv_cash = vanna_sv_cash
        self.charm_cash = charm_cash
        self.dkurt_cash = dkurt_cash
        self.underlying_price = underlying_price

    def to_dict(self) -> dict:
        """
        Converts the instance to a dictionary.

        :return: A dictionary representation of the instance
        """
        return {
            "delta": self.delta,
            "investor_id": self.investor_id,
            "delta_cash": self.delta_cash,
            "gamma_p_cash": self.gamma_p_cash,
            "vega_cash": self.vega_cash,
            "theta_cash": self.theta_cash,
            "db_cash": self.db_cash,
            "vanna_vs_cash": self.vanna_vs_cash,
            "vanna_sv_cash": self.vanna_sv_cash,
            "charm_cash": self.charm_cash,
            "underlying_price": self.underlying_price
        }