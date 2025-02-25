import os
from abc import ABC, abstractmethod

from typing import Optional

from ctp.market_data_manager import MarketDataManager
from model.config.exchange_config import ExchangeConfig
from model.direction import Direction


class Exchange(ABC):
    def __init__(self, account_config: ExchangeConfig, config_file_path: str):
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

    def is_login(self):
        return True if self.trader_user_spi is not None and self.trader_user_spi.login_finish else False

    def is_query_finish(self, query_name: str):
        return self.trader_user_spi.query_finish[query_name]

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
    def insert_order(self, instrument_id: str, direction: Direction, price, volume) -> Optional[str]:
        pass

    @abstractmethod
    def order_action(self, instrument_id: str, order_ref: str):
        pass

    @abstractmethod
    def subscribe_market_data(self, instrument_ids):
        pass

    @abstractmethod
    def query_investor_position(self, instrument_id: Optional[str]):
        pass

    @abstractmethod
    def query_investor_position_detail(self):
        pass

    @abstractmethod
    def init_market_data(self, market_data_manager: MarketDataManager):
        pass
