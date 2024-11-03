import configparser
import logging
import time
from uuid import uuid4
from helper.helper import TIMEOUT
from memory.memory_manager import MemoryManager
from model.config.exchange_config import ExchangeConfig
from model.direction import Direction
from model.exchange.cff_exchange import CFFExchange
from model.exchange.exchange_base import Exchange
from model.enum.exchange_type import ExchangeType
from model.exchange.se_exchange import SExchange
from typing import Dict

logging.basicConfig(level=logging.INFO)

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
        self.user_id = uuid4()
        self.user_name = self.config.get('USER', 'Name')
        print(f'切换{self.user_name}')
        self.exchange_config: Dict[str, ExchangeConfig] = {}
        # exchange_config = {
        #   "CFFEX": {
        #       "BrokerName": "",
        #       "BrokerID: "",
        #       ...
        #   },
        #   "SE": {
        #       ...
        #   }
        # }
        self.exchanges: Dict[str, Exchange] = {}
        # exchange = {
        #   "CFFEX": CFFEXExchange(),
        #   "SE": SSEExchange()
        # }

        for section in self.config.sections():
            if section in [e.name for e in ExchangeType]:
                self.exchange_config[section] = ExchangeConfig(
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

        # 内存中心
        self.memory: MemoryManager = MemoryManager()

    def query_instrument(self):
        for exchange_id, exchange in self.exchanges.items():
            if not exchange.is_login():
                continue
            exchange.query_instrument()
            while not self.is_query_finish(exchange_id):
                time.sleep(3)
            logging.info(f"{self.user_name} 的 {exchange_id} 合约查询完成")

    def init_exchange(self, config_file_root: str):
        for exchange_id, config in self.exchange_config.items():
            try:
                exchange = None
                path = f"{config_file_root}/{self.user_name}/{exchange_id}/"
                if exchange_id == ExchangeType.CFFEX.name:
                    exchange = CFFExchange(config, path, self.memory)
                elif exchange_id == ExchangeType.SE.name:
                    exchange = SExchange(config, path, self.memory)
                else:
                    logging.warning(f"未知的交易所类型: {exchange_id}")

                if exchange:
                    self.exchanges[exchange_id] = exchange
                    logging.info(f"用户 {self.user_name} 的 {exchange_id} 交易所初始化成功")
            except Exception as e:
                logging.error(f"初始化交易所 {exchange_id} 时出现错误: {e}")


    def connect_exchange(self):
        for exchange_id, exchange in self.exchanges.items():
            logging.info(f"正在连接 {self.user_name} 的交易所：{exchange_id}")
            start_time = time.time()
            exchange.connect_market_data()
            exchange.connect_trader()
            while not self.is_login(exchange_id):
                if time.time() - start_time > TIMEOUT:
                    logging.error(f'{exchange_id} 登录超时')
                    break
                time.sleep(3)
            else:
                # 若登录成功，记录成功日志
                logging.info(f'{self.user_name} 的 {exchange_id} 登录成功')
                continue

            logging.warning(f"跳过未成功连接的交易所：{self.user_name}的{ExchangeType[exchange_id].value}")

    def init_memory(self):
        for exchange_id, exchange in self.exchanges.items():
            exchange.init_memory()


    def is_login(self, exchange_id: str) -> bool:
        return self.exchanges[exchange_id].is_login()

    def is_query_finish(self, exchange_id: str) -> bool:
        return self.exchanges[exchange_id].trader_user_spi.query_finish

    # 批量订阅
    def subscribe_market_data(self):
        print('开始订阅行情')

        for exchange_id, exchange in self.exchanges.items():
            if not exchange.is_login():
                continue
            instrument_ids = list(exchange.trader_user_spi.subscribe_instrument.keys())
            # 将 instrument_ids 分成每组 100 个
            batch_size = 100
            for i in range(0, len(instrument_ids), batch_size):
                batch = instrument_ids[i:i + batch_size]  # 每组 100 个
                exchange.subscribe_market_data(batch)  # 订阅每组的数据
                # print(f"订阅 {exchange_id} 的合约批次: {batch}")

        print('已发送全部订阅请求')


    def query_investor_position(self, exchange_id: str):
        print(f'查询投资者{ExchangeType[exchange_id].value}持仓')
        if exchange_id in self.exchanges:
            exchange = self.exchanges[exchange_id]
            exchange.query_investor_position()

    def query_investor_position_detail(self, exchange_id: str):
        print(f'查询投资者{ExchangeType[exchange_id].value}持仓细节')
        if exchange_id in self.exchanges:
            exchange = self.exchanges[exchange_id]
            exchange.query_investor_position_detail()

    def insert_order(self, exchange_id: str, instrument_id: str, direction: Direction, limit_price: float, volume: int):
        print(f'报单{ExchangeType[exchange_id].value}')
        if exchange_id in self.exchanges:
            self.exchanges[exchange_id].insert_order(instrument_id, direction, limit_price, volume)







