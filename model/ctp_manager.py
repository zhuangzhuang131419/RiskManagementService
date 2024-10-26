import os.path
import time
from queue import Queue
from threading import Thread

from memory.memory_manager import MemoryManager
from model.exchange.exchange import Exchange
from model.exchange.exchange_type import ExchangeType
from model.instrument.instrument import Future
from model.instrument.option import Option
from model.user import User
from helper.helper import *


class CTPManager:

    CONFIG_FILE_PATH = '../con_file/'

    current_user = None

    users = {}

    def __init__(self):
        self.market_data = Queue()
        self.init_user()
        if not os.path.exists(self.CONFIG_FILE_PATH):
            os.makedirs(self.CONFIG_FILE_PATH)

    def init_user(self):
        for root, _, files in os.walk("config"):
            for file_name in files:
                if file_name.endswith('.ini'):
                    user = User(os.path.join(root, file_name))
                    self.users[user.user_id] = user



    def init_exchange(self, exchange_type):
        # 登录
        self.current_user.connect_exchange(exchange_type.name)
        start_time = time.time()
        while not self.current_user.is_login(exchange_type.name):
            if time.time() - start_time > TIMEOUT:
                print(f'{exchange_type.value}登录超时')
                return
            time.sleep(3)

        print(f'{exchange_type.value}登录成功')

        # 查询合约
        self.current_user.query_instrument(exchange_type.name)
        while not self.current_user.is_query_finish(exchange_type.name):
            time.sleep(3)

        # 获取订阅的合约ID列表
        instrument_ids = list(self.current_user.exchanges[exchange_type.name].trader_user_spi.exchange_id.keys())
        print(f'当前{exchange_type.value}订阅的合约数量为:{len(instrument_ids)}')

        # 初始化内存
        self.current_user.memory = MemoryManager(self.current_user.exchanges[exchange_type.name].trader_user_spi.expire_date)
        # 把内存传给交易中心
        self.current_user.exchanges[exchange_type.name].market_data_user_spi.set_memory_manager(self.current_user.memory)

        self.current_user.subscribe_market_data(exchange_type.name, instrument_ids)


    def switch_to_user(self, user_id: str):
        self.current_user = self.users[user_id]

        threads = []
        for exchange_type in ExchangeType:
            t = Thread(target=self.init_exchange, args=(exchange_type,))
            threads.append(t)
            t.start()
            time.sleep(1)

        for t in threads:
            t.join()

        print("用户切换成功")



    def tick(self):
        while True:
            depth_market_date = self.current_user.memory.market_data.get(True)

            # update_time = depth_market_date.UpdateTime
            instrument_id = depth_market_date.InstrumentID
            # 清洗编码问题，数据分类：-1为编码错误

            if filter_index_future(instrument_id) or filter_index_option(instrument_id):
                market_data_list = [round(time.time()), depth_market_date.BidPrice1, depth_market_date.BidVolume1, depth_market_date.AskPrice1, depth_market_date.AskVolume1, 0]
                for i, data in enumerate(market_data_list):
                    # 遍历所有的行情字段，判断是否double最大值
                    if (isinstance(data, int) or isinstance(data, float)) and (abs(data - 1.7976931348623157e+308) < 0.000001):
                        market_data_list[i] = -1

                market_data_list = [market_data_list[0], round(market_data_list[1], 1), int(market_data_list[2]), round(market_data_list[3], 3), int(market_data_list[4]), 0]

                # 判断是否可交易
                if depth_market_date.BidVolume1 >= 1 and depth_market_date.AskVolume1 >= 1 and depth_market_date.BidPrice1 > 0 and depth_market_date.AskPrice1 > 0:
                    market_data_list[5] = 1
                else:
                    market_data_list[5] = 0

                if filter_index_option(instrument_id):
                    # 导入期权行情
                    try:
                        o = Option(instrument_id, "")
                        l1 = self.current_user.memory.option_manager.index_option_month_forward_id.index(o.symbol)
                        l2 = OPTION_PUT_CALL_DICT[o.option_type]
                        l3 = self.current_user.memory.option_manager.option_series_dict[o.symbol].get_all_strike_price().index(o.strike_price)
                        self.current_user.memory.option_manager.index_option_market_data[l1, l2, l3, 1:7] = market_data_list[:6]
                    except ValueError as e:
                        print(f"ValueError: {e} - Couldn't find the symbol or strike price in the list. instrument: {instrument_id}")
                    except Exception as e:
                        print(f"Exception: {e} - instrument id: {instrument_id}")
                        continue
                elif filter_index_future(instrument_id):
                    # 导入期货行情
                    f = Future(instrument_id, "")
                    try:
                        l1 = self.current_user.memory.future_manager.index_future_month_id.index(f.symbol)
                        self.current_user.memory.future_manager.index_future_market_data[l1, 0:6] = market_data_list[:6]
                    except ValueError as e:
                        print(f"ValueError: {e} - Couldn't find the symbol in the list. future: {f}")
                    except Exception as e:
                        print(f"Exception: {e} - instrument id: {depth_market_date.InstrumentID}")
                        continue
            else:
                # 非订阅行情
                continue



    #
    #
    # def query_investor_position:







    