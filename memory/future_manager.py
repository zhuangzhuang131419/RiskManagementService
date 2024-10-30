from operator import index

from typing import Dict

from model.instrument.instrument import Future, validate_future_id


class FutureManager:
    # 期货合约
    index_futures_dict: Dict[str, Future] = {}

    # 把来自交易所的instrument_id 映射到我们自己的symbol
    instrument_transform_full_symbol: Dict[str, str] = {}

    # 3*4 [IH2410,IH2411,IH2412,IH2503,IF2410,IF2411,IF2412,IF2503,IM2410,IM2411,IM2412,IM2503]
    # 合成唯一的期货月份列表
    index_future_month_id = []

    def __init__(self, index_futures:[Future]):
        self.init_index_future_dict(index_futures)
        self.init_index_future_month_id()


    def init_index_future_dict(self, index_futures:[Future]):
        for future in index_futures:
            if future.symbol not in self.index_futures_dict:
                self.index_futures_dict[future.symbol] = future
            self.instrument_transform_full_symbol[future.id] = future.full_symbol

        print(f"instrument_transform_symbol: {self.instrument_transform_full_symbol}")


    def init_index_future_month_id(self):
        """
        生成唯一的期货月份列表，格式如：['IH2410', 'IH2411', 'IF2410', 'IM2412', ...]
        """
        unique_month_ids = set()
        for future_symbol in self.index_futures_dict.keys():
            unique_month_ids.add(future_symbol)
        self.index_future_month_id = sorted(list(unique_month_ids))
