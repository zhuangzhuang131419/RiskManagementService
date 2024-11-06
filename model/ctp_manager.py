import os.path
import time
import logging
from queue import Queue
from threading import Thread, Lock
from typing import Dict
from model.config.exchange_config import ExchangeConfig
from model.enum.baseline_type import BaselineType
from model.memory.market_data import DepthMarketData
from model.user import User
from helper.helper import *

logging.basicConfig()


class CTPManager:

    CONFIG_FILE_PATH = 'con_file'



    current_user : User = None

    users : Dict[str, User] = {}

    baseline : BaselineType = BaselineType.INDIVIDUAL

    def __init__(self):
        if not os.path.exists(self.CONFIG_FILE_PATH):
            os.makedirs(self.CONFIG_FILE_PATH)
        self._lock = Lock()
        self.market_data: Queue = Queue()
        self.init_user()
        self.connect_users()


    def init_user(self):
        try:
            for root, _, files in os.walk("config"):
                for file_name in files:
                    if file_name.endswith('.ini'):
                        user = User(os.path.join(root, file_name))
                        self.users[user.user_name] = user
                        logging.info(f"用户 {user.user_name} 初始化完成")
        except Exception as e:
            logging.error(f"初始化用户时出现错误: {e}")

    def connect_users(self):
        threads = []
        for user in self.users.values():
            t = Thread(target=self.connect_user, args=(user,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    def connect_user(self, user: User):
        user.init_exchange(self.CONFIG_FILE_PATH)
        user.connect_exchange()
        user.query_instrument()
        user.subscribe_market_data()
        user.init_memory()

    def switch_to_user(self, user_name: str) -> bool:
        with self._lock:
            self.current_user = self.users.get(user_name, None)
            if self.current_user is not None:
                logging.info(f"当前用户切换为：{user_name}")
                return True
            else:
                logging.warning(f"未找到用户：{user_name}")
                return False


    def tick(self):
        while True:
            depth_market_date: DepthMarketData = self.current_user.memory.market_data.get(True)

            # update_time = depth_market_date.UpdateTime
            full_symbol = depth_market_date.symbol
            # 清洗编码问题，数据分类：-1为编码错误

            if filter_index_option(full_symbol) or filter_etf_option(full_symbol):
                # 导入期权行情
                try:
                    symbols = full_symbol.split('-')
                    symbol = symbols[0]
                    option_type = symbols[1]
                    strike_price = float(symbols[-1])
                except IndexError:
                    print(f"full_symbol:{full_symbol}")
                    raise IndexError

                if option_type == 'C':
                    self.current_user.memory.option_series_dict[symbol].strike_price_options[strike_price].call.market_data = depth_market_date
                elif option_type == 'P':
                    self.current_user.memory.option_series_dict[symbol].strike_price_options[strike_price].put.market_data = depth_market_date
            elif filter_index_future(full_symbol):
                # 导入期货行情
                symbol = full_symbol.split('-')[0]
                self.current_user.memory.index_futures_dict[symbol].market_data = depth_market_date
            else:
                print(f"exception: {depth_market_date}")





    #
    #
    # def query_investor_position:







    