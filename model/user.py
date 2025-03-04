import json
import time
from uuid import uuid4

from utils.api import ReqQryInvestorPosition, ReqOrderInsert, ReqOrderAction, ReqQryInstrument
from utils.helper import TIMEOUT
from ctp.market_data_manager import MarketDataManager
from memory.user_memory_manager import UserMemoryManager
from model.config.exchange_config import ExchangeConfig
from model.direction import Direction
from ctp.exchange.cff_exchange import CFFExchange
from ctp.exchange.exchange_base import Exchange
from model.enum.exchange_type import ExchangeType
from ctp.exchange.se_exchange import SExchange
from typing import Dict, Optional, List
from utils.logger import Logger


class User:
    def __init__(self, config_path: str, market_data_manager: MarketDataManager):
        self.logger = Logger(__name__).logger
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            self.logger.error(f"Configuration file {config_path} not found.")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON configuration file {config_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading configuration file {config_path}: {e}")
            raise
        self.user_id = uuid4()
        self.user_name = self.config["Name"]

        self.exchange_config: Dict[ExchangeType, List[ExchangeConfig]] = {}

        self.exchanges: Dict[ExchangeType, List[Exchange]] = {}

        # investor_id 具体属于哪个交易所
        self.investors: Dict[str, ExchangeType] = {}

        for exchange_type in ExchangeType:
            if exchange_type.name in self.config:
                exchange_configs : List[ExchangeConfig] = []
                for config in self.config[exchange_type.name]:
                    exchange_config = ExchangeConfig(config)
                    exchange_configs.append(exchange_config)
                    self.investors[exchange_config.investor_id] = exchange_type
                self.exchange_config[exchange_type] = exchange_configs

        # 内存中心
        self.user_memory = UserMemoryManager(self.user_name, self.exchange_config)
        self.market_data_memory = market_data_manager

    def get_exchange(self, exchange_type: ExchangeType, investor_id: str):
        if exchange_type in self.exchanges:
            exchange_list = self.exchanges[exchange_type]
            for exchange in exchange_list:
                if exchange.config.investor_id == investor_id:
                    return exchange
        return None

    def connect_master_data(self):
        for exchange_type, exchange_list in self.exchanges.items():
            self.logger.info(f"正在连接 {self.user_name} 的交易所：{exchange_type.value}")
            start_time = time.time()
            for exchange in exchange_list:
                exchange.connect_market_data()
                exchange.connect_trader()
                while not exchange.is_market_login():
                    if time.time() - start_time > TIMEOUT:
                        self.logger.error(f'{exchange_type.value} 登录超时')
                        break
                else:
                    # 若登录成功，记录成功日志
                    self.logger.info(f'{exchange_type.value} 登录成功')
                    continue

                self.logger.info(f"跳过未成功连接的交易所：{exchange_type.value}")


    def query_instrument(self):
        for exchange_type, exchange_list in self.exchanges.items():
            # 查询exchange type下面exchange list的一个就可以了
            for exchange in exchange_list:
                if not exchange.is_trade_login():
                    continue
                exchange.query_instrument()
                while not exchange.is_trade_query_finish(ReqQryInstrument):
                    time.sleep(3)
                self.logger.info(f"{self.user_name} 的 {exchange_type.value} 合约查询完成")
                break


    def init_exchange(self, config_file_root: str):
        for exchange_type, configs in self.exchange_config.items():
            try:
                exchange_list: List[Exchange] = []
                for config in configs:
                    path = f"{config_file_root}/{self.user_name}/{exchange_type.name}/{config.investor_id}/"
                    if exchange_type == ExchangeType.CFFEX:
                        exchange_list.append(CFFExchange(config, path, self.user_memory, self.market_data_memory))
                    elif exchange_type == ExchangeType.SE:
                        exchange_list.append(SExchange(config, path, self.user_memory, self.market_data_memory))
                    else:
                        self.logger.error(f"未知的交易所类型: {exchange_type.value}")


                if len(exchange_list) > 0:
                    self.exchanges[exchange_type] = exchange_list
                    self.logger.info(f"用户 {self.user_name} 的 {exchange_type.value} 交易所初始化成功")
            except Exception as e:
                self.logger.error(f"初始化交易所 {exchange_type.value} 时出现错误: {e}")


    def connect_trade(self):
        for exchange_type, exchange_list in self.exchanges.items():
            self.logger.info(f"正在连接 {self.user_name} 的交易所：{exchange_type.value}")

            for exchange in exchange_list:
                start_time = time.time()
                exchange.connect_trader()
                while not exchange.is_trade_login():
                    if time.time() - start_time > TIMEOUT:
                        self.logger.error(f'{exchange_type.value} investor_id: {exchange.config.investor_id} 登录超时')
                        break
                else:
                    # 若登录成功，记录成功日志
                    self.logger.info(f'{self.user_name} 的 {exchange_type.value} investor_id: {exchange.config.investor_id} 登录成功')
                    continue
                self.logger.warning(f"跳过未成功连接的交易所：{self.user_name}的{exchange_type.value} investor_id: {exchange.config.investor_id}")

    def init_market_memory(self):
        for exchange_id, exchange_list in self.exchanges.items():
            exchange_list[0].init_market_data(self.market_data_memory)

    # 批量订阅
    def subscribe_market_data(self):
        self.logger.info('开始订阅行情')

        for exchange_id, exchange_list in self.exchanges.items():
            for exchange in exchange_list:
                if not exchange.is_market_login():
                    continue
                instrument_ids = list(exchange.trader_user_spi.subscribe_instrument.keys())
                # 将 instrument_ids 分成每组 100 个
                batch_size = 100
                for i in range(0, len(instrument_ids), batch_size):
                    batch = instrument_ids[i:i + batch_size]  # 每组 100 个
                    exchange.subscribe_market_data(batch)  # 订阅每组的数据
                break
            self.logger.info('已发送全部订阅请求')

    def query_investor_position(self):
        self.user_memory.refresh_position()
        for exchange_id, exchange_list in self.exchanges.items():
            for exchange in exchange_list:
                self.query_investor_position_by_exchange(exchange_id, exchange.config.investor_id, None, 30)

    def query_investor_position_by_exchange(self, exchange_type: ExchangeType, investor_id: str, instrument_id: Optional[str], timeout=TIMEOUT) -> bool:
        exchange = self.get_exchange(exchange_type, investor_id)
        if exchange is None:
            self.logger.error(f"找不到exchange")
            return False
        if not exchange.is_trade_login():
            self.logger.error(f"{exchange}未登录")
            return False

        self.logger.info(f'查询投资者{exchange.config.investor_id}持仓')

        start_time = time.time()
        exchange.query_investor_position(instrument_id)
        while not exchange.is_trade_query_finish(ReqQryInvestorPosition):
            if time.time() - start_time > timeout:
                self.logger.error(f'{exchange_type.value} {ReqQryInvestorPosition} 查询超时')
                return False
        return True

    def query_investor_position_detail(self, exchange_type: ExchangeType, timeout=TIMEOUT) -> bool:
        self.logger.info(f'查询投资者{exchange_type.value}持仓细节')
        if exchange_type in self.exchanges:
            exchange_list = self.exchanges[exchange_type]
            if not all(exchange.is_trade_login() for exchange in exchange_list):
                return False

            for exchange in exchange_list:
                start_time = time.time()
                exchange.query_investor_position_detail()
                while not exchange.is_trade_query_finish(ReqQryInvestorPosition):
                    if time.time() - start_time > timeout:
                        self.logger.error(f'{exchange_type.value} {ReqQryInvestorPosition} 查询超时')
                        return False
            return True

    def insert_order(self, exchange_type: ExchangeType, investor_id: str, instrument_id: str, direction: Direction, limit_price: float, volume: int, timeout=TIMEOUT) -> Optional[str]:
        self.logger.info(f'报单{exchange_type.value} {investor_id}')
        exchange = self.get_exchange(exchange_type, investor_id)

        if exchange is None:
            self.logger.error(f"找不到exchange")
            return None

        if not exchange.is_trade_login():
            self.logger.error(f"{exchange}未登录")
            return None

        return exchange.insert_order(instrument_id, direction, limit_price, volume)

    def order_action(self, exchange_type: ExchangeType, investor_id: str, instrument_id: str, order_ref: str, timeout=TIMEOUT) -> bool:
        self.logger.info(f'撤单{exchange_type.value}')

        exchange = self.get_exchange(exchange_type, investor_id)

        if exchange is None:
            self.logger.error(f"找不到exchange")
            return False

        if not exchange.is_trade_login():
            self.logger.error(f"{exchange}未登录")
            return False

        exchange.order_action(instrument_id, order_ref)
        return True








