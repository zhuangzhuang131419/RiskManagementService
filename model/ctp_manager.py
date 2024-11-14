import os.path
import time
import logging
from queue import Queue
from threading import Thread, Lock
from typing import Dict

from memory.market_data_manager import MarketDataManager
from model.config.exchange_config import ExchangeConfig
from model.enum.baseline_type import BaselineType
from model.memory.market_data import DepthMarketData
from model.user import User
from helper.helper import *


class CTPManager:

    CONFIG_FILE_PATH = 'con_file'

    current_user : User = None

    # 用作获取行情数据
    market_data_user : User = None

    # 行情内存
    market_data_manager: MarketDataManager = MarketDataManager()

    # 普通的users
    users : Dict[str, User] = {}

    baseline : BaselineType = BaselineType.SH

    timestamp : time

    def __init__(self):
        if not os.path.exists(self.CONFIG_FILE_PATH):
            os.makedirs(self.CONFIG_FILE_PATH)

        user_config_path = []

        try:
            for root, _, files in os.walk("config"):
                for file_name in files:
                    if not file_name.endswith('.ini'):
                        continue
                    user_config_path.append(os.path.join(root, file_name))
        except Exception as e:
            print(f"初始化用户时出现错误: {e}")

        # 随机挑选一个连接行情
        self.market_data_user = User(user_config_path[0], self.market_data_manager)

        # 先获取行情
        self.connect_market_data()

        # 连接各个user
        self.init_user(user_config_path)
        self.connect_trader()


    def init_user(self, user_config_path):

        for config_path in user_config_path:
            user = User(config_path, self.market_data_manager)
            self.users[user.user_name] = user
            print(f"用户 {user.user_name} 初始化完成")


    def connect_market_data(self):
        """
        连接行情中心
        """
        print('连接行情中心')
        self.market_data_user.init_exchange(self.CONFIG_FILE_PATH)
        self.market_data_user.connect_master_data()
        self.market_data_user.query_instrument()
        self.market_data_user.init_market_memory()
        self.market_data_user.subscribe_market_data()
        print('行情初始化结束')

    def connect_trader(self):
        print('连接交易中心')
        for user in self.users.values():
            user.init_exchange(self.CONFIG_FILE_PATH)
            user.connect_trade()

    def switch_to_user(self, user_name: str) -> bool:
        self.current_user = self.users.get(user_name, None)
        if self.current_user is not None:
            print(f"当前用户切换为：{user_name}")
            for exchange in self.current_user.exchanges.keys():
                self.current_user.query_investor_position(exchange, None)
            return True
        else:
            print(f"未找到用户：{user_name}")
            return False








    