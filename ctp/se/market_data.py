import copy

from api_se import ThostFtdcApiSOpt
from api_se.ThostFtdcApiSOpt import CThostFtdcRspInfoField, CThostFtdcRspUserLoginField
from helper.helper import *
from queue import Queue


class MarketData(ThostFtdcApiSOpt.CThostFtdcMdSpi):

    def __init__(self, market_data_user_api, config):
        super().__init__()
        self.market_data_user_api = market_data_user_api
        self.config = config
        self.market_data = Queue()
        self.memory_manager = None

    def set_memory_manager(self, memory_manager):
        self.memory_manager = memory_manager

    # 当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用
    def OnFrontConnected(self):
        print("开始建立行情连接")


        login_field = ThostFtdcApiSOpt.CThostFtdcReqUserLoginField()

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
    def OnRspUserLogin(self, pRspUserLogin: CThostFtdcRspUserLoginField, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool):
        if pRspInfo.ErrorID != 0 and pRspInfo is not None:
            print('行情连接失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('行情账户登录成功！')

    # SubscribeMarketData
    def OnRspSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID != 0:
            print(f"订阅行情失败，合约: {pSpecificInstrument.InstrumentID}, 错误信息: {pRspInfo.ErrorMsg}")
        # else:
        #     if not is_index_option(pSpecificInstrument.InstrumentID) and not is_index_future(pSpecificInstrument.InstrumentID):
        #         print(f"订阅合约 {pSpecificInstrument.InstrumentID} 成功")

    # 深度行情通知
    def OnRtnDepthMarketData(self, pDepthMarketData):
        if filter_etf(pDepthMarketData.InstrumentID):
            print('SSEX OnRtnDepthMarketData')
            print(pDepthMarketData)
            self.memory_manager.market_data.put(copy.copy(pDepthMarketData))








