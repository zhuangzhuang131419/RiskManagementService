import numpy as np
from numpy.core.records import ndarray

from model.instrument.instrument import Future


class FutureManager:
    # 期货合约
    index_futures = []

    # 3*4 [IH2410,IH2411,IH2412,IH2503,IF2410,IF2411,IF2412,IF2503,IM2410,IM2411,IM2412,IM2503]
    # 合成唯一的期货月份列表
    index_future_month_id = []

    # 期货行情结构
    # 将期货的行情信息记录在此结构中，2维度的numpy，按顺序记录：字段时间，bid,bidv,ask,askv,avail 6个字段
    # bid,bidv,ask,askv,avail 代表：买1价格，买1量，卖1价格，卖1量，是否可交易标记
    index_future_market_data: ndarray

    def __init__(self, index_futures:[Future]):
        self.index_futures = index_futures
        self.init_index_future_month_id()
        self.init_index_option_market_data()

    def init_index_future_month_id(self):
        """
        生成唯一的期货月份列表，格式如：['IH2410', 'IH2411', 'IF2410', 'IM2412', ...]
        """
        unique_month_ids = set()
        for future in self.index_futures:
            unique_month_ids.add(future.id[:6])
        self.index_future_month_id = sorted(list(unique_month_ids))

    def init_index_option_market_data(self):
        """

        :return:
        """
        self.index_future_market_data = np.zeros((len(self.index_future_month_id), 6))
