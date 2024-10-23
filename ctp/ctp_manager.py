import os.path
import time

from api_cffex import ThostFtdcApi
from api_sse import ThostFtdcApiSOpt
from config.config_manager import ConfigManager
from ctp.cffex.market_data import MarketData
from ctp.exchange.cffex_exchange import CFFEXExchange
from ctp.exchange.sse_exchange import SSEExchange
from memory.memory_manager import MemoryManager
from model.instrument.instrument import Future
from model.instrument.option import Option
from ctp.cffex.trader import Trader
from helper.helper import *


class CTPManager:


    # 内存中心
    memory : MemoryManager

    CONFIG_FILE_PATH = '../con_file/'


    def __init__(self):
        self.login_config = ConfigManager().login_config
        if not os.path.exists(self.CONFIG_FILE_PATH):
            os.makedirs(self.CONFIG_FILE_PATH)

        self.sse_exchange = SSEExchange(ConfigManager('../config/sse_config.ini'))
        self.cffex_exchange = CFFEXExchange(ConfigManager('../config/cffex_config.ini'))



    def tick(self):
        while True:
            depth_market_date = self.cffex_exchange.market_data_user_spi.market_data.get(True)

            # update_time = depth_market_date.UpdateTime
            instrument_id = depth_market_date.InstrumentID
            # 清洗编码问题，数据分类：-1为编码错误

            if is_index_future(instrument_id) or is_index_option(instrument_id):
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

                if is_index_option(instrument_id):
                    # 导入期权行情
                    try:
                        o = Option(instrument_id, "")
                        l1 = self.memory.option_manager.index_option_month_forward_id.index(o.symbol)
                        l2 = OPTION_PUT_CALL_DICT[o.option_type]
                        l3 = self.memory.option_manager.option_series_dict[o.symbol].get_all_strike_price().index(o.strike_price)
                        self.memory.option_manager.index_option_market_data[l1, l2, l3, 1:7] = market_data_list[:6]
                    except ValueError as e:
                        print(f"ValueError: {e} - Couldn't find the symbol or strike price in the list. instrument: {instrument_id}")
                    except Exception as e:
                        print(f"Exception: {e} - instrument id: {instrument_id}")
                        continue
                elif is_index_future(instrument_id):
                    # 导入期货行情
                    f = Future(instrument_id, "")
                    try:
                        l1 = self.memory.future_manager.index_future_month_id.index(f.symbol)
                        self.memory.future_manager.index_future_market_data[l1, 0:6] = market_data_list[:6]
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







    