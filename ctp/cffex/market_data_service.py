import copy
import time

from api_cffex import ThostFtdcApi
from api_cffex.ThostFtdcApi import CThostFtdcRspInfoField, CThostFtdcRspUserLoginField, CThostFtdcDepthMarketDataField
from helper.helper import *
from queue import Queue

from model.memory.market_data import DepthMarketData


class MarketDataService(ThostFtdcApi.CThostFtdcMdSpi):

    def __init__(self, market_data_user_api, account_config):
        super().__init__()
        self.market_data_user_api = market_data_user_api
        self.config = account_config
        self.market_data = Queue()
        self.memory_manager = None

    def set_memory_manager(self, memory_manager):
        self.memory_manager = memory_manager

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
            # print(f"订阅合约 {pSpecificInstrument.InstrumentID} 成功")

    # 深度行情通知
    def OnRtnDepthMarketData(self, pDepthMarketData: CThostFtdcDepthMarketDataField) -> "void":

        if filter_index_future(pDepthMarketData.InstrumentID) or filter_index_option(pDepthMarketData.InstrumentID):
            if self.memory_manager is not None:

                depth_market_data = DepthMarketData()
                depth_market_data.time = time.time()
                depth_market_data.ask_volumes[0] = int(pDepthMarketData.AskVolume1)
                depth_market_data.bid_volumes[0] = int(pDepthMarketData.BidVolume1)
                depth_market_data.ask_prices[0] = round(pDepthMarketData.AskPrice1, 2)
                depth_market_data.bid_prices[0] = round(pDepthMarketData.BidPrice1, 2)
                depth_market_data.exchange_id = pDepthMarketData.ExchangeID
                depth_market_data.instrument_id = pDepthMarketData.InstrumentID

                depth_market_data.clean_data()
                depth_market_data.set_available()
                self.memory_manager.market_data.put(depth_market_data)









