from operator import index

from typing import Dict

from model.instrument.instrument import Future, validate_future_id


class FutureManager:



    def __init__(self):
        self.index_futures_dict: Dict[str, Future] = {}
        self.index_future_symbol = []
        # 把来自交易所的instrument_id 映射到我们自己的symbol
        self.instrument_transform_full_symbol: Dict[str, str] = {}

    def add_index_future(self, index_futures:[Future]):
        for future in index_futures:
            if future.symbol not in self.index_futures_dict:
                self.index_futures_dict[future.symbol] = future
            self.instrument_transform_full_symbol[future.id] = future.full_symbol
            self.index_future_symbol.append(future.symbol)

    def transform_instrument_id(self, instrument_id: str):
        try:
            result = self.instrument_transform_full_symbol[instrument_id]
            return result
        except ValueError:
            print(f"instrument_id:{instrument_id}")
            raise ValueError