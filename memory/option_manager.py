import numpy as np
from model.instrument import Option

class OptionManager:
    # 期权
    index_options = list()

    # 期权行权价
    option_month_strike_id = []

    # 期权品种月份列表
    index_option_month_forward_id = []

    # 期权品种月份行权价数量
    index_option_month_strike_num = []

    # 期权行情结构
    index_option_market_data = []

    def __init__(self, index_options: [Option]):
        self.index_options = index_options
        self.index_option_month_forward_id = self.init_index_option_month_id()
        self.index_option_month_strike_num = self.init_index_option_month_strike_num()

    def init_index_option_month_id(self):
        """
        生成唯一的期权月份列表，格式如：["HO2410","HO2411","HO2412","HO2501","HO2503","HO2506",…,…]
        """
        unique_month_ids = set()
        for option in self.index_options:
            unique_month_ids.add(option.id[:6])

        return sorted(list(unique_month_ids))

    def init_index_option_month_strike_num(self):
        """
        生成每个期权品种月份对应的行权价数量列表。
        假设期权格式为：'HO2410-C-4100'，表示品种HO，月份2410，行权价4100
        """
        strike_price_count = {}
        for option in self.index_options:
            # 提取品种和月份部分，例如 'HO2410-C-4100' 提取 'HO2410'
            # 统计每个品种和月份的行权价数量
            if option.symbol in strike_price_count:
                strike_price_count[option.symbol] += 1
            else:
                strike_price_count[option.symbol] = 1

        # 将字典中的数量转化为列表
        return sorted(list(strike_price_count.values()))

    def init_index_option_market_data(self):
        np.zeros((len(self.index_option_month_forward_id), 2, self.index_option_month_strike_num, 7))



