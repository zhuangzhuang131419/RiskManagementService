from select import select

from model.instrument import Future


class FutureManager:
    # 期货合约
    index_futures = list()

    # 3*4 [IH2410,IH2411,IH2412,IH2503,IF2410,IF2411,IF2412,IF2503,IM2410,IM2411,IM2412,IM2503]
    # 合成唯一的期货月份列表
    index_future_month_id = list()

    # 期货行情结构
    index_future_market_data = list()

    def __init__(self, index_futures:[Future]):
        self.index_futures = index_futures
        self.index_future_month_id = self.init_index_future_month_id()

    def init_index_future_month_id(self):
        """
        生成唯一的期货月份列表，格式如：['IH2410', 'IH2411', 'IF2410', 'IM2412', ...]
        """
        unique_month_ids = set()
        for future in self.index_futures:
            unique_month_ids.add(future.id[:6])

        return sorted(list(unique_month_ids))
