from typing import Dict

from helper.helper import filter_index_future, filter_etf_option, filter_index_option
from model.enum.exchange_type import ExchangeType
from model.position import Position


class UserMemoryManager:
    def __init__(self):
        self.order_ref = 0
        self.position: Dict[str, Position]= {}


    def get_order_ref(self):
        order_ref = str(self.order_ref).zfill(12)
        self.order_ref += 1
        return order_ref

    def refresh_se_position(self):
        for symbol in self.position.keys():
            if filter_etf_option(symbol):
                del self.position[symbol]

    def refresh_cffex_position(self):
        for symbol in self.position.keys():
            if filter_index_future(symbol) or filter_index_option(symbol):
                del self.position[symbol]

