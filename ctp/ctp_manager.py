import os.path
import time
from threading import Thread
from typing import Dict

from ctp.market_data_manager import MarketDataManager
from model.user import User
from utils.helper import *


class CTPManager:

    CONFIG_FILE_PATH = 'con_file'

    current_user : User = None

    # 用作获取行情数据
    market_data_user : User = None

    # 行情内存
    market_data_manager: MarketDataManager = MarketDataManager()

    # 普通的users
    users : Dict[str, User] = {}

    timestamp : time

    white_list = ["80050672", "9980050672",
                  "80533506", "9980533506",
                  "85334525", "9985334525",
                  "82106867", "9982106867",
                  "26800491", "9926800491",
                  "80039190", "9980039190",
                  "80039277", "9980039277",
                  "82105958", "9982105958",
                  "0081500056", "9982100962"]

    def __init__(self, env):
        if not os.path.exists(self.CONFIG_FILE_PATH):
            os.makedirs(self.CONFIG_FILE_PATH)

        user_config_path = []

        try:
            for root, _, files in os.walk("config"):
                for file_name in files:
                    if not file_name.endswith('.json'):
                        continue
                    if not file_name.startswith(env):
                        continue
                    user_config_path.append(os.path.join(root, file_name))
        except Exception as e:
            print(f"初始化用户时出现错误: {e}")



        # 连接各个user
        self.init_user(user_config_path)


        # 查询持仓
        self.query_position()

        Thread(target=self.market_data_manager.index_volatility_calculator).start()
        Thread(target=self.run_daily_job).start()

    def query_position(self):
        for user in self.users.values():
            user.query_investor_position()

    def run_daily_job(self):
        while True:
            now = datetime.datetime.now()
            # 设置目标时间为今天的 9 点
            target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)

            # 如果当前时间已经过了目标时间，则设为明天的 9 点
            if now > target_time:
                target_time += datetime.timedelta(days=1)

            # 计算需要等待的时间（秒）
            wait_time = (target_time - now).total_seconds()

            print(f"距离下一次执行还有 {wait_time} 秒")

            # 等待直到目标时间
            time.sleep(wait_time)

            print(f"执行daily job")

            # 执行 daily_job
            self.market_data_manager.refresh()
            self.market_data_user.query_instrument()
            self.market_data_user.init_market_memory()
            self.market_data_user.subscribe_market_data()

    def check_white_list(self):
        print("检查白名单")
        for exchange_type, exchanges in self.market_data_user.exchange_config.items():
            if any(exchange.user_id not in self.white_list for exchange in exchanges):
                red_print(f"未在白名单: {[exchange.app_id for exchange in exchanges]}")
                return False
        print("检查白名单通过")
        return True

    def init_user(self, user_config_path):
        try:
            # 随机挑选一个连接行情
            self.market_data_user = User(user_config_path[0], self.market_data_manager)
            if not self.check_white_list():
                return

            # 先获取行情
            self.connect_market_data()
            self.users[self.market_data_user.user_name] = self.market_data_user
            print(f"用户 {self.market_data_user.user_name} 初始化完成")
        except Exception as e:
            print(f"初始化行情用户失败: {e}")
            raise

        print('-------------------------行情连接完毕----------------------------')


        for config_path in user_config_path[1:]:
            user = User(config_path, self.market_data_manager)
            self.users[user.user_name] = user
            print(f"用户 {user.user_name} 初始化完成")
            user.init_exchange(self.CONFIG_FILE_PATH)
            user.connect_trade()

        print("------------------------用户连接完毕-----------------------------")

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

    def switch_to_user(self, user_name: str) -> bool:
        self.current_user = self.users.get(user_name, None)
        if self.current_user is not None:
            print(f"当前用户切换为：{user_name}")
            print(f"当前持仓信息：{self.current_user.user_memory.print_position()}")
            return True
        else:
            print(f"未找到用户：{user_name}")
            return False








    