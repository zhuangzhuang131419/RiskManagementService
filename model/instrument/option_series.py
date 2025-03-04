import math
from datetime import datetime
from typing import Dict, TypeVar, Generic


from utils.helper import count_trading_days, HOLIDAYS, YEAR_TRADING_DAY
from model.enum.option_type import OptionType
from model.instrument.option import Option, OptionTuple
from model.memory.atm_volatility import ATMPram
from model.memory.imply_price import ImplyPrice
from model.memory.wing_model_para import WingModelPara

class OptionSeries:

    def __init__(self, symbol: str, options: [Option]):
        """
        初始化期权系列。

        :param symbol: 期权的名字，例如 'HO-2410' 表示某个品种（HO）和月份（2410）的期权系列。
        :param options: 期权对象列表，包含该系列的所有期权。
        """
        self.symbol = symbol # 期权名字，例如 'HO2410' '005020241225'
        self.strike_price_options: Dict[float, OptionTuple] = {}
        self.expired_date = symbol[-8:]

        for option in options:
            if option.strike_price not in self.strike_price_options:
                self.strike_price_options[option.strike_price] = OptionTuple()

            if option.is_call_option():
                self.strike_price_options[option.strike_price].set_call(option)
            elif option.is_put_option():
                self.strike_price_options[option.strike_price].set_put(option)

        # self.strike_price_options = dict(sorted(self.strike_price_options.items()))

        # 数据结构
        self.imply_price = ImplyPrice()
        self.atm_volatility = ATMPram()
        self.wing_model_para = WingModelPara()
        self.customized_wing_model_para = WingModelPara()


    def get_option(self, strike_price, option_type: OptionType) -> Option:
        if option_type == OptionType.P:
            return self.strike_price_options[strike_price].put
        else:
            return self.strike_price_options[strike_price].call

    def get_all_strike_price(self):
        return list(self.strike_price_options.keys())

    def get_num_strike_price(self):
        return len(self.strike_price_options.keys())

    def __str__(self):
        return f"OptionSeries: {self.symbol}"


