import configparser
import logging
import time
from uuid import uuid4

from helper.api import ReqQryInvestorPosition, ReqOrderInsert, ReqOrderAction
from helper.helper import TIMEOUT
from memory.market_data_manager import MarketDataManager
from memory.user_memory_manager import UserMemoryManager
from model.config.exchange_config import ExchangeConfig
from model.direction import Direction
from ctp.exchange.cff_exchange import CFFExchange
from ctp.exchange.exchange_base import Exchange
from model.enum.exchange_type import ExchangeType
from ctp.exchange.se_exchange import SExchange
from typing import Dict, Optional

class User:
    def __init__(self, config_path: str, market_data_manager: MarketDataManager):
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

        self.exchange_config: Dict[ExchangeType, ExchangeConfig] = {}

        self.exchanges: Dict[ExchangeType, Exchange] = {}

        sections = self.config.sections()

        for exchange_type in ExchangeType:
            section = exchange_type.name
            if section in sections:
                self.exchange_config[exchange_type] = ExchangeConfig(
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
        self.user_memory = UserMemoryManager(self.user_name)
        self.market_data_memory = market_data_manager

    def connect_master_data(self):
        for exchange_type, exchange in self.exchanges.items():
            print(f"正在连接 {self.user_name} 的交易所：{exchange_type.value}")
            start_time = time.time()
            exchange.connect_market_data()
            exchange.connect_trader()
            while not self.is_login(exchange_type):
                if time.time() - start_time > TIMEOUT:
                    logging.error(f'{exchange_type.value} 登录超时')
                    break
                time.sleep(3)
            else:
                # 若登录成功，记录成功日志
                print(f'{exchange_type.value} 登录成功')
                continue

            print(f"跳过未成功连接的交易所：{exchange_type.value}")

    def query_instrument(self):
        for exchange_type, exchange in self.exchanges.items():
            if not exchange.is_login():
                continue
            exchange.query_instrument()
            while not self.is_query_finish(exchange_type, 'ReqQryInstrument'):
                time.sleep(3)
            print(f"{self.user_name} 的 {exchange_type.value} 合约查询完成")

    def init_exchange(self, config_file_root: str):
        for exchange_type, config in self.exchange_config.items():
            try:
                exchange = None
                path = f"{config_file_root}/{self.user_name}/{exchange_type.name}/"
                if exchange_type == ExchangeType.CFFEX:
                    exchange = CFFExchange(config, path, self.user_memory, self.market_data_memory)
                elif exchange_type == ExchangeType.SE:
                    exchange = SExchange(config, path, self.user_memory, self.market_data_memory)
                else:
                    logging.warning(f"未知的交易所类型: {exchange_type.value}")

                if exchange:
                    self.exchanges[exchange_type] = exchange
                    print(f"用户 {self.user_name} 的 {exchange_type.value} 交易所初始化成功")
            except Exception as e:
                logging.error(f"初始化交易所 {exchange_type.value} 时出现错误: {e}")


    def connect_trade(self):
        for exchange_type, exchange in self.exchanges.items():
            logging.info(f"正在连接 {self.user_name} 的交易所：{exchange_type.value}")
            start_time = time.time()
            exchange.connect_trader()
            while not self.is_login(exchange_type):
                if time.time() - start_time > TIMEOUT:
                    logging.error(f'{exchange_type.value} 登录超时')
                    break
                time.sleep(3)
            else:
                # 若登录成功，记录成功日志
                logging.info(f'{self.user_name} 的 {exchange_type.value} 登录成功')
                continue

            logging.warning(f"跳过未成功连接的交易所：{self.user_name}的{exchange_type.value}")

    def init_market_memory(self):
        for exchange_id, exchange in self.exchanges.items():
            exchange.init_market_data(self.market_data_memory)


    def is_login(self, exchange_type: ExchangeType) -> bool:
        return self.exchanges[exchange_type].is_login()

    def is_query_finish(self, exchange_type: ExchangeType, query_name: str) -> bool:
        return self.exchanges[exchange_type].trader_user_spi.query_finish[query_name]

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

    def query_investor_position(self):
        for exchange_id, exchange in self.exchanges.items():
            if not exchange.is_login():
                continue
            self.query_investor_position_by_exchange(exchange_id, None)

    def query_investor_position_by_exchange(self, exchange_type: ExchangeType, instrument_id: Optional[str], timeout=TIMEOUT) -> bool:
        print(f'查询投资者{exchange_type.value}持仓')
        if exchange_type in self.exchanges:
            exchange = self.exchanges[exchange_type]
            if not exchange.is_login():
                print(f"{exchange_type.value}未登录")
                return False
            start_time = time.time()
            exchange.query_investor_position(instrument_id)
            while not self.is_query_finish(exchange_type, ReqQryInvestorPosition):
                if time.time() - start_time > timeout:
                    logging.error(f'{exchange_type.value} {ReqQryInvestorPosition} 查询超时')
                    return False
                time.sleep(3)
        return True

    def query_investor_position_detail(self, exchange_type: ExchangeType) -> bool:
        print(f'查询投资者{exchange_type.value}持仓细节')
        if exchange_type in self.exchanges:
            exchange = self.exchanges[exchange_type]
            if not exchange.is_login():
                return False
            exchange.query_investor_position_detail()
            return True

    def insert_order(self, exchange_type: ExchangeType, instrument_id: str, direction: Direction, limit_price: float, volume: int, timeout=TIMEOUT) -> Optional[str]:
        print(f'报单{exchange_type.value}')
        if exchange_type in self.exchanges:
            exchange = self.exchanges[exchange_type]
            if not exchange.is_login():
                print(f"{exchange_type.value}未登录")
                return None
            start_time = time.time()
            order_ref = exchange.insert_order(instrument_id, direction, limit_price, volume)
            while not self.is_query_finish(exchange_type, ReqOrderInsert):
                if time.time() - start_time > timeout:
                    logging.error(f'{exchange_type.value} {ReqOrderInsert} 查询超时')
                    return order_ref
                time.sleep(3)
            return order_ref
        return None


    def order_action(self, exchange_type: ExchangeType, instrument_id: str, order_ref: str, timeout=TIMEOUT) -> bool:
        print(f'撤单{exchange_type.value}')
        if exchange_type in self.exchanges:
            exchange = self.exchanges[exchange_type]
            if not exchange.is_login():
                print(f"{exchange_type.value}未登录")
                return False
            start_time = time.time()
            self.exchanges[exchange_type].order_action(instrument_id, order_ref)
            while not self.is_query_finish(exchange_type, ReqOrderAction):
                if time.time() - start_time > timeout:
                    logging.error(f'{exchange_type.value} {ReqOrderAction} 查询超时')
                    return False
                time.sleep(3)
            return True
        return False








