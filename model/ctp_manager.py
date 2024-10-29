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
from model.memory.market_data import MarketData
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
        instrument_ids = list(self.current_user.exchanges[exchange_type.name].trader_user_spi.subscribe_instrument.keys())
        print(f'当前{exchange_type.value}订阅的合约数量为:{len(instrument_ids)}')




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

        # 初始化内存
        self.current_user.memory.init_cffex_instrument(self.current_user.exchanges[ExchangeType.CFFEX.name].trader_user_spi.subscribe_instrument)

        # se_instruments = {}
        #
        # for key, value in self.current_user.exchanges[ExchangeType.SSE.name].trader_user_spi.subscribe_instrument:
        #     se_instruments[key] = value
        # for key, value in self.current_user.exchanges[ExchangeType.SSE.name].trader_user_spi.subscribe_instrument:
        #     se_instruments[key] = value

        # 合并上交所 深交所的instrument
        se_instruments = {**self.current_user.exchanges[ExchangeType.SSE.name].trader_user_spi.subscribe_instrument, **self.current_user.exchanges[ExchangeType.SZSE.name].trader_user_spi.subscribe_instrument}

        print(f"上交所深交所共有{len(se_instruments)}个合约")

        self.current_user.memory.init_se_instrument(se_instruments)

        for exchange_type in ExchangeType:
            if self.current_user.is_login(exchange_type.name):
                # 把内存传给交易中心
                self.current_user.exchanges[exchange_type.name].market_data_user_spi.set_memory_manager(self.current_user.memory)

                # 批量订阅数据
                instrument_ids = list(self.current_user.exchanges[exchange_type.name].trader_user_spi.subscribe_instrument.keys())
                self.current_user.subscribe_batches_market_data(exchange_type.name, instrument_ids)




    def tick(self):
        while True:
            depth_market_date = self.current_user.memory.market_data.get(True)
            print(f'tick：{depth_market_date}')

            # update_time = depth_market_date.UpdateTime
            instrument_id = depth_market_date.InstrumentID
            # 清洗编码问题，数据分类：-1为编码错误

            if filter_index_future(instrument_id) or filter_index_option(instrument_id):
                market_data_list = [round(time.time()), depth_market_date.bid_prices[0], depth_market_date.bid_volumes[0], depth_market_date.ask_prices[0], depth_market_date.ask_volumes[0], 0]


                for i, data in enumerate(market_data_list):
                    # 遍历所有的行情字段，判断是否double最大值
                    if (isinstance(data, int) or isinstance(data, float)) and (abs(data - 1.7976931348623157e+308) < 0.000001):
                        market_data_list[i] = -1

                # market_data_list = [market_data_list[0], round(market_data_list[1], 1), int(market_data_list[2]), round(market_data_list[3], 3), int(market_data_list[4]), 0]

                market_data = MarketData()
                market_data.time = market_data_list[0]
                market_data.bid_prices[0] = round(market_data_list[1], 1)
                market_data.bid_volumes[0] = int(market_data_list[2])
                market_data.ask_prices[0] = round(market_data_list[3], 3)
                market_data.ask_volumes[0] = int(market_data_list[4])

                # 判断是否可交易
                if depth_market_date.BidVolume1 >= 1 and depth_market_date.AskVolume1 >= 1 and depth_market_date.BidPrice1 > 0 and depth_market_date.AskPrice1 > 0:
                    market_data_list[5] = 1
                    market_data.available = 1
                else:
                    market_data_list[5] = 0
                    market_data.available = 0

                if filter_index_option(instrument_id):
                    # 导入期权行情
                    try:
                        o = Option(instrument_id, "", "")
                        l1 = self.current_user.memory.cffex_option_manager.index_option_month_forward_id.index(o.symbol)
                        l2 = OPTION_PUT_CALL_DICT[o.option_type]
                        l3 = self.current_user.memory.cffex_option_manager.option_series_dict[o.symbol].get_all_strike_price().index(o.strike_price)
                        self.current_user.memory.cffex_option_manager.index_option_market_data[l1, l2, l3, 1:7] = market_data_list[:6]

                        if OPTION_PUT_CALL_DICT[o.option_type] == 0:
                            # call
                            self.current_user.memory.cffex_option_manager.option_series_dict[o.symbol].strike_price_options[o.strike_price].call.market_data = market_data
                        elif OPTION_PUT_CALL_DICT[o.option_type] == 1:
                            # put
                            self.current_user.memory.cffex_option_manager.option_series_dict[o.symbol].strike_price_options[o.strike_price].put.market_data = market_data
                    except ValueError as e:
                        print(f"ValueError: {e} - Couldn't find the symbol or strike price in the list. instrument: {instrument_id}")
                    except Exception as e:
                        print(f"Exception: {e} - instrument id: {instrument_id}")
                        continue
                elif filter_index_future(instrument_id):
                    # 导入期货行情
                    f = Future(instrument_id, "", "")
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
                if depth_market_date.exchang_id == ExchangeType.SSE.name or depth_market_date.exchang_id == ExchangeType.SZSE.name:
                    symbol = instrument_id.split('-')[0]
                    option_type = instrument_id.split('-')[1]
                    strike_price = float(instrument_id.split('-')[-1])

                    if option_type == 1:
                        self.current_user.memory.se_option_manager.option_series_dict[symbol].strike_price_options[strike_price].call.market_data = depth_market_date
                    elif option_type == 2:
                        self.current_user.memory.se_option_manager.option_series_dict[symbol].strike_price_options[strike_price].put.market_data = depth_market_date





    #
    #
    # def query_investor_position:







    