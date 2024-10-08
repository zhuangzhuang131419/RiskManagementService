from collections import OrderedDict

import numpy as np
from numpy.core.records import ndarray
from numpy.f2py.rules import options

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

    # 最多数量的行权价
    index_option_month_strike_max_num = 0

    # 期权行情结构
    # 第一个维度：品种月份维度，顺序与期权品种月份列表对齐，[0, : , : , : ]代表HO2410
    # 第二个维度：固定大小为2，看涨or 看跌，看涨期权为0，看跌期权为1
    # 第三个维度：行权价维度
    # 第四个维度：字段维度固定大写为7，七个字段存放内容为：行权价，字段时间，bid, bidv, ask, askv, avail
    # 例如要取HO2410的看涨期权的第一个行权价的bid价格，index_option_market_data[0, 0, 0, 2]
    index_option_market_data = ndarray

    def __init__(self, index_options: [Option]):
        self.index_options = index_options
        self.init_index_option_month_id()
        self.init_index_option_month_strike_num()
        self.index_option_market_data = self.init_index_option_market_data()

    def init_index_option_month_id(self):
        """
        生成唯一的期权月份列表，格式如：["HO2410","HO2411","HO2412","HO2501","HO2503","HO2506",…,…]
        """
        unique_month_ids = set()
        for option in self.index_options:
            unique_month_ids.add(option.id[:6])

        self.index_option_month_forward_id = sorted(list(unique_month_ids))

    def init_index_option_month_strike_num(self):
        """
        生成每个期权品种月份对应的行权价数量列表。
        假设期权格式为：'HO2410-C-4100'，表示品种HO，月份2410，行权价4100
        """
        strike_price_count = dict()
        for option in self.index_options:
            # 提取品种和月份部分，例如 'HO2410-C-4100' 提取 'HO2410'
            # 统计每个品种和月份的行权价数量
            if option.symbol in strike_price_count:
                strike_price_count[option.symbol] += 1
            else:
                strike_price_count[option.symbol] = 1
        print(strike_price_count)
        sorted_keys = sorted(strike_price_count.keys())
        self.index_option_month_strike_num = [strike_price_count[key] for key in sorted_keys]
        self.index_option_month_strike_max_num = max(self.index_option_month_strike_num)

    def init_index_option_market_data(self):
        """
        
        :return: 
        """

        # 假设有 len(self.index_option_month_forward_id) 个月份，每个期权品种最多有 2 种看涨/看跌期权，index_option_month_strike_num 个行权价，每个行权价有 7 个字段
        market_data = np.zeros((len(self.index_option_month_forward_id), 2, self.index_option_month_strike_max_num, 7))
        return market_data








