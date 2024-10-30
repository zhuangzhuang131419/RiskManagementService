import os.path
import time
from queue import Queue
from threading import Thread

from numba.cpython.setobj import set_intersection

from helper.calculator import is_close
from memory.memory_manager import MemoryManager
from model.exchange.exchange import Exchange
from model.exchange.exchange_type import ExchangeType
from model.instrument.instrument import Future
from model.instrument.option import Option
from model.memory.market_data import MarketData, DepthMarketData
from model.user import User
from helper.helper import *


class CTPManager:

    CONFIG_FILE_PATH = '../con_file/'

    current_user = None

    users = {}

    def __init__(self):
        self.market_data: Queue = Queue()
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
        instrument_ids = list(self.current_user.exchanges[exchange_type.name].trader_user_spi.subscribe_instrument.keys())
        print(f'当前{exchange_type.value}订阅的合约数量为:{len(instrument_ids)}')




    def switch_to_user(self, user_id: str):
        self.current_user: User = self.users[user_id]

        threads = []
        for exchange_type in ExchangeType:
            t = Thread(target=self.init_exchange, args=(exchange_type,))
            threads.append(t)
            t.start()
            time.sleep(1)

        for t in threads:
            t.join()

        print("用户切换成功")

        # 初始化内存
        self.current_user.memory.init_cffex_instrument(self.current_user.exchanges[ExchangeType.CFFEX.name].trader_user_spi.subscribe_instrument)

        # 合并上交所 深交所的instrument
        se_instruments = {**self.current_user.exchanges[ExchangeType.SSE.name].trader_user_spi.subscribe_instrument, **self.current_user.exchanges[ExchangeType.SZSE.name].trader_user_spi.subscribe_instrument}

        print(f"上交所深交所共有{len(se_instruments)}个合约")

        self.current_user.memory.init_se_instrument(se_instruments)

        for exchange_type in ExchangeType:
            if self.current_user.is_login(exchange_type.name):
                # 把内存传给交易中心
                self.current_user.exchanges[exchange_type.name].market_data_user_spi.set_memory_manager(self.current_user.memory)
                self.current_user.exchanges[exchange_type.name].market_data_user_spi.set_memory_manager(self.current_user.memory)

                # 批量订阅数据
                instrument_ids = list(self.current_user.exchanges[exchange_type.name].trader_user_spi.subscribe_instrument.keys())
                self.current_user.subscribe_batches_market_data(exchange_type.name, instrument_ids)




    def tick(self):
        while True:
            depth_market_date: DepthMarketData = self.current_user.memory.market_data.get(True)

            # update_time = depth_market_date.UpdateTime
            full_symbol = depth_market_date.symbol
            # 清洗编码问题，数据分类：-1为编码错误

            if filter_index_option(full_symbol):
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
                    self.current_user.memory.cffex_option_manager.option_series_dict[symbol].strike_price_options[strike_price].call.market_data = depth_market_date
                elif option_type == 'P':
                    self.current_user.memory.cffex_option_manager.option_series_dict[symbol].strike_price_options[strike_price].put.market_data = depth_market_date
            elif filter_index_future(full_symbol):
                # 导入期货行情
                symbol = full_symbol.split('-')[0]
                self.current_user.memory.future_manager.index_futures_dict[symbol].market_data = depth_market_date

            elif filter_etf(full_symbol):
                    symbols = full_symbol.split('-')
                    symbol = symbols[0]
                    option_type = symbols[1]
                    strike_price = float(symbols[-1])

                    if option_type == 'C':
                        self.current_user.memory.se_option_manager.option_series_dict[symbol].strike_price_options[strike_price].call.market_data = depth_market_date
                    elif option_type == 'P':
                        self.current_user.memory.se_option_manager.option_series_dict[symbol].strike_price_options[strike_price].put.market_data = depth_market_date
            else:
                print(f"exception: {depth_market_date}")





    #
    #
    # def query_investor_position:







    