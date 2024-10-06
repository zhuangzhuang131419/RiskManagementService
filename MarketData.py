from CTP_API import ThostFtdcApi
from CTP_API.ThostFtdcApi import CThostFtdcRspInfoField, CThostFtdcRspUserLoginField, CThostFtdcMulticastInstrumentField
from ConfigManager import ConfigManager
from Helper import *


class MarketData(ThostFtdcApi.CThostFtdcMdSpi):

    sub_product_ids = []
    exchangeId = dict()

    def __init__(self, market_data_user_api):
        super().__init__()
        self.sub_product_ids = None
        self.config_manager = ConfigManager()
        self.market_data_user_api = market_data_user_api

    # 当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用
    def OnFrontConnected(self):
        print("开始建立行情连接")

        login_info = self.config_manager.get_login_info()
        login_field = ThostFtdcApi.CThostFtdcReqUserLoginField()

        login_field.BrokerID = login_info['BrokerID']
        login_field.UserID = login_info['UserID']
        login_field.Password = login_info['Password']

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


        # subIds = [id.encode('utf-8') for id in ["SA209"]]
        subIds = ["IF2412"]
        # print(subIds)
        ret = self.market_data_user_api.SubscribeMarketData(subIds)

        if ret == 0:
            print('发送订阅合约请求成功！')
        else:
            print('发送订阅合约请求失败！')
            judge_ret(ret)

    # SubscribeMarketData
    def OnRspSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID != 0:
            print(f"订阅行情失败，合约: {pSpecificInstrument.InstrumentID}, 错误信息: {pRspInfo.ErrorMsg}")
        else:
            print(f"订阅合约 {pSpecificInstrument.InstrumentID} 成功")

    # 深度行情通知
    def OnRtnDepthMarketData(self, pDepthMarketData):
        print("OnRtnDepthMarketData")
        print(f'{pDepthMarketData.InstrumentID}:{pDepthMarketData.LastPrice}')








