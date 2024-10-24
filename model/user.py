import configparser
import time
import os

from psutil import users

from model.config.account_config import AccountConfig
from model.exchange.cff_exchange import CFFExchange
from model.exchange.exchange_type import ExchangeType
from model.exchange.ss_exchange import SSExchange


class User:
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
        print(f'切换{self.user_id}')
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
            if section == ExchangeType.CFFEX.value or section == ExchangeType.SSEX.value:
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
        print(f'accounts={self.accounts}')

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

        if account_id == ExchangeType.CFFEX.value:
            exchange = CFFExchange(self.accounts[account_id])
        elif account_id == ExchangeType.SSEX.value:
            exchange = SSExchange(self.accounts[account_id])

        print(f'exchange{exchange}')
        self.exchanges[account_id] = exchange
        exchange.connect_market_data()
        exchange.connect_trader()

        print(f'Exchanges = {self.exchanges}')

    def is_login(self, account_id: str):
        return self.exchanges[account_id].trader_user_spi.login_finish

    def is_query_finish(self, account_id: str):
        return self.exchanges[account_id].trader_user_spi.query_finish







