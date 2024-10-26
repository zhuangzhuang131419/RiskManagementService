import configparser
import time
import os

from psutil import users

from memory.memory_manager import MemoryManager
from model.config.account_config import AccountConfig
from model.exchange.cff_exchange import CFFExchange
from model.exchange.exchange_type import ExchangeType
from model.exchange.ss_sz_exchange import SSSZExchange


class User:

    # 内存中心
    memory : MemoryManager


    def __init__(self, config_path: str):
        self.config = configparser.ConfigParser()

        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                self.config.read_file(file)
        except FileNotFoundError:
            print(f"Configuration file {config_path} not found.")
            raise
        except Exception as e:
            print(f"Error reading configuration file {config_path}: {e}")
            raise
        self.user_id = self.config.get('USER', 'UserID')
        self.user_name = self.config.get('USER', 'Name')
        print(f'切换{self.user_name}')
        self.accounts = {}
        # accounts = {
        #   "CFFEX": {
        #       "BrokerName": "",
        #       "BrokerID: "",
        #       ...
        #   },
        #   "SSE": {
        #       ...
        #   }
        # }
        self.exchanges = {}
        # exchange = {
        #   "CFFEX": CFFEXExchange(),
        #   "SSE": SSEExchange()
        # }

        for section in self.config.sections():
            if section == ExchangeType.CFFEX.name or section == ExchangeType.SSE.name or section == ExchangeType.SZSE.name:
                self.accounts[section] = AccountConfig(
                    broker_name=self.config.get(section, 'BrokerName'),
                    broker_id=self.config.get(section, 'BrokerID'),
                    user_id=self.config.get(section, 'UserID'),
                    investor_id=self.config.get(section, 'InvestorID'),
                    password=self.config.get(section, 'Password'),
                    app_id=self.config.get(section, 'AppID'),
                    auth_code=self.config.get(section, 'AuthCode'),
                    market_server_front=self.config.get(section, 'MarketServerFront'),
                    trade_server_front=self.config.get(section, 'TradeServerFront')
                )
        print(f'accounts={len(self.accounts)}')

    def query_instrument(self, account_id: str):
        """
        连接 account_id 对应的合约
        """
        exchange = self.exchanges[account_id]
        exchange.query_instrument()

    def connect_exchange(self, account_id: str):
        """
        连接 account_id 对应的交易所
        """

        exchange = None

        if account_id == ExchangeType.CFFEX.name:
            exchange = CFFExchange(self.accounts[account_id], "con_file/ss_sz/")
        elif account_id == ExchangeType.SSE.name:
            exchange = SSSZExchange(self.accounts[account_id], "con_file/ss/", exchange_type=ExchangeType.SSE)
        elif account_id == ExchangeType.SZSE.name:
            exchange = SSSZExchange(self.accounts[account_id], "con_file/sz/", exchange_type=ExchangeType.SZSE)

        self.exchanges[account_id] = exchange
        # print(f'共需要连接{len(self.exchanges)}个交易所')
        exchange.connect_market_data()
        exchange.connect_trader()

    def is_login(self, account_id: str) -> bool:
        return self.exchanges[account_id].trader_user_spi.login_finish

    def is_query_finish(self, account_id: str) -> bool:
        return self.exchanges[account_id].trader_user_spi.query_finish

    # 批量订阅
    def subscribe_batches_market_data(self, account_id, instrument_ids: [str]):
        print('开始订阅行情')

        page_size = 100
        for i in range(0, len(instrument_ids), page_size):
            page = instrument_ids[i:i + page_size]  # 获取当前分页
            self.subscribe_market_data(account_id, page)  # 处理当前分页的订阅

        print('已发送全部订阅请求')

    def subscribe_market_data(self, account_id: str, instrument_ids):
        if account_id in self.exchanges:
            exchange = self.exchanges[account_id]
            exchange.subscribe_market_data(instrument_ids)







