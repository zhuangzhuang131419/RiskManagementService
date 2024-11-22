from typing import Dict

from helper.helper import filter_index_future, filter_etf_option, filter_index_option
from model.enum.exchange_type import ExchangeType
from model.position import Position


class UserMemoryManager:
    def __init__(self, user_name: str):
        self.order_ref = 0
        self.positions: Dict[str, Position]= {}
        self.user = user_name


    def get_order_ref(self):
        order_ref = str(self.order_ref).zfill(12)
        self.order_ref += 1
        return order_ref

    def refresh_se_position(self):
        # 只保留不符合 filter_etf_option 条件的键值对
        self.positions = {symbol: value for symbol, value in self.positions.items() if not filter_etf_option(symbol)}

    def refresh_cffex_position(self):
        # 只保留不符合 filter_index_future 和 filter_index_option 条件的键值对
        self.positions = {symbol: value for symbol, value in self.positions.items() if not (filter_index_future(symbol) or filter_index_option(symbol))}

    def print_position(self) -> str:
        if not self.positions:
            return "No positions available."
        return "\n".join(
            f"{key}: {position}" for key, position in self.positions.items()
        )




