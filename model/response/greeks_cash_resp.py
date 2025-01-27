from typing import List, Union


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

    def __mul__(self, other: Union[float, int]) -> 'GreeksCashResp':
        """
        Overloads the * operator to multiply all numeric fields by a scalar.
        """
        if not isinstance(other, (float, int)):
            raise TypeError("Multiplication is only supported with float or int")

        return GreeksCashResp(
            delta=self.delta * other,
            investor_id=self.investor_id,
            delta_cash=self.delta_cash * other,
            gamma_p_cash=self.gamma_p_cash * other,
            vega_cash=self.vega_cash * other,
            theta_cash=self.theta_cash * other,
            db_cash=self.db_cash * other,
            vanna_vs_cash=self.vanna_vs_cash * other,
            vanna_sv_cash=self.vanna_sv_cash * other,
            charm_cash=self.charm_cash * other,
            dkurt_cash=self.dkurt_cash * other,
            underlying_price=self.underlying_price * other
        )

    def __add__(self, other: 'GreeksCashResp') -> 'GreeksCashResp':
        """
        Overloads the + operator to add two GreeksCashResp objects.

        :param other: Another instance of GreeksCashResp
        :return: A new GreeksCashResp instance with summed values
        """
        if not isinstance(other, GreeksCashResp):
            raise TypeError("The object to add must be an instance of GreeksCashResp")

        return GreeksCashResp(
            delta=self.delta + other.delta,
            delta_cash=self.delta_cash + other.delta_cash,
            gamma_p_cash=self.gamma_p_cash + other.gamma_p_cash,
            vega_cash=self.vega_cash + other.vega_cash,
            theta_cash=self.theta_cash + other.theta_cash,
            db_cash=self.db_cash + other.db_cash,
            vanna_vs_cash=self.vanna_vs_cash + other.vanna_vs_cash,
            vanna_sv_cash=self.vanna_sv_cash + other.vanna_sv_cash,
            charm_cash=self.charm_cash + other.charm_cash,
            dkurt_cash=self.dkurt_cash + other.dkurt_cash,
        )

    @classmethod
    def sum(cls, items: List['GreeksCashResp']) -> 'GreeksCashResp':
        if not items:
            return cls()  # Return an empty instance with all values set to None

        result = items[0]
        for item in items[1:]:
            result += item

        return result