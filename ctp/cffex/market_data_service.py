import copy
import time

from api_cffex import ThostFtdcApi
from api_cffex.ThostFtdcApi import CThostFtdcRspInfoField, CThostFtdcRspUserLoginField, CThostFtdcDepthMarketDataField
from helper.helper import *
from queue import Queue

from memory.memory_manager import MemoryManager
from model.memory.market_data import DepthMarketData


class MarketDataService(ThostFtdcApi.CThostFtdcMdSpi):
    memory_manager: MemoryManager = None
    def __init__(self, market_data_user_api, account_config, market_data_manager: MemoryManager):
        super().__init__()
        self.market_data_user_api = market_data_user_api
        self.config = account_config
        self.market_data = Queue()
        self.memory_manager = market_data_manager


    # 当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用
    def OnFrontConnected(self):
        print("开始建立行情连接")


        login_field = ThostFtdcApi.CThostFtdcReqUserLoginField()

        login_field.BrokerID = self.config.broker_id
        login_field.UserID = self.config.user_id
        login_field.Password = self.config.password

        ret = self.market_data_user_api.ReqUserLogin(login_field, 0)

        if ret == 0:
            print('发送用户登录行情账户请求成功！')
        else:
            print('发送用户登录行情账户请求失败！')
            judge_ret(ret)

    # ReqUserLogin
    def OnRspUserLogin(self, pRspUserLogin: 'CThostFtdcRspUserLoginField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
        if pRspInfo.ErrorID != 0 and pRspInfo is not None:
            print('行情连接失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('行情账户登录成功！')

    # SubscribeMarketData
    def OnRspSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID != 0:
            print(f"订阅行情失败，合约: {pSpecificInstrument.InstrumentID}, 错误信息: {pRspInfo.ErrorMsg}")
        # else:
            print(f"订阅合约 {pSpecificInstrument.InstrumentID} 成功")

    # 深度行情通知
    def OnRtnDepthMarketData(self, pDepthMarketData: CThostFtdcDepthMarketDataField) -> "void":
        if self.memory_manager is not None:
            if pDepthMarketData.InstrumentID in self.memory_manager.instrument_transform_full_symbol:

                if pDepthMarketData.InstrumentID == "HO2412-C-2400":
                    print(pDepthMarketData.AskPrice1)

                depth_market_data = DepthMarketData()
                depth_market_data.time = round(time.time())
                depth_market_data.ask_volumes[0] = int(pDepthMarketData.AskVolume1)
                depth_market_data.bid_volumes[0] = int(pDepthMarketData.BidVolume1)
                depth_market_data.ask_prices[0] = round(pDepthMarketData.AskPrice1, 2)
                depth_market_data.bid_prices[0] = round(pDepthMarketData.BidPrice1, 2)

                if pDepthMarketData.InstrumentID not in self.memory_manager.instrument_transform_full_symbol:
                    raise ValueError(f"收到异常行情数据{pDepthMarketData.InstrumentID}")
                    return
                else:
                    depth_market_data.symbol = self.memory_manager.instrument_transform_full_symbol[pDepthMarketData.InstrumentID]

                depth_market_data.clean_data()
                depth_market_data.set_available()

                if filter_index_option(depth_market_data.symbol):
                    symbol, option_type, strike_price = parse_option_full_symbol(depth_market_data.symbol)
                    if option_type == OptionType.C:
                        self.memory_manager.option_series_dict[symbol].strike_price_options[
                            strike_price].call.market_data = depth_market_data
                    elif option_type == OptionType.P:
                        self.memory_manager.option_series_dict[symbol].strike_price_options[strike_price].put.market_data = depth_market_data
                elif filter_index_future(depth_market_data.symbol):
                    symbol = depth_market_data.symbol.split('-')[0]
                    if symbol in self.memory_manager.index_futures_dict:
                        self.memory_manager.index_futures_dict[symbol].market_data = depth_market_data









