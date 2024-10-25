import os
from abc import ABC, abstractmethod
from statistics import pstdev

from model.config.account_config import AccountConfig
from model.direction import Direction


class Exchange(ABC):
    def __init__(self, account_config: AccountConfig, config_file_path: str):
        # 参数
        self.config = account_config
        # 交易所类型
        self.type = None

        # 行情中心
        self.market_data_user_spi = None
        self.market_data_user_api = None

        # 交易中心
        self.trader_user_api = None
        self.trader_user_spi = None

        # 配置文件
        self.config_file_path = config_file_path
        if not os.path.exists(config_file_path):
            os.makedirs(config_file_path)

    @abstractmethod
    def connect_market_data(self):
        pass

    @abstractmethod
    def connect_trader(self):
        pass

    @abstractmethod
    def query_instrument(self):
        pass

    @abstractmethod
    def insert_order(self, code: str, direction: Direction, price, volume, strategy_id = 0):
        pass

    @abstractmethod
    def subscribe_market_data(self, instrument_ids):
        pass
