from abc import ABC, abstractmethod

from config.config_manager import ConfigManager
from model.direction import Direction


class Exchange(ABC):
    def __init__(self, config: ConfigManager):
        # 参数
        self.login_config = config.login_config()
        self.server_config = config.server_config()

        # 行情中心
        self.market_data_user_spi = None
        self.market_data_user_api = None

        # 交易中心
        self.trader_user_api = None
        self.trader_user_spi = None

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
