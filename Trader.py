from CTP_API import ThostFtdcApi
from CTP_API.ThostFtdcApi import CThostFtdcRspInfoField, CThostFtdcRspUserLoginField, \
    CThostFtdcMulticastInstrumentField, CThostFtdcInstrumentField
from ConfigManager import ConfigManager
from Helper import *

class Trader(ThostFtdcApi.CThostFtdcTraderSpi):
    # 指数期货的品种列表
    Index_Future_ProductIDlist = ['IH', 'IF', 'IM']
    # 指数期权的品种列表
    Index_Option_ProductIDlist = ['HO', 'IO', 'MO']

    sub_product_ids = Index_Future_ProductIDlist + Index_Option_ProductIDlist
    exchangeId = dict()
    expire_date = dict()

    def __init__(self, trader_user_api):
        super().__init__()
        self.config_manager = ConfigManager()
        self.trader_user_api = trader_user_api
        self.login_info = self.config_manager.get_login_info()


    def OnFrontConnected(self):
        print("开始建立交易连接")
        auth_field = ThostFtdcApi.CThostFtdcReqAuthenticateField()


        auth_field.BrokerID = self.login_info['BrokerID']
        auth_field.UserID = self.login_info['UserID']
        auth_field.Password = self.login_info['Password']
        auth_field.AuthCode = self.login_info['AuthCode']

        ret = self.trader_user_api.ReqAuthenticate(auth_field, 0)
        if ret == 0:
            print('发送穿透式认证请求成功！')
        else:
            print('发送穿透式认证请求失败！')
            judge_ret(ret)

    def OnRspAuthenticate(self, pRspAuthenticateField: "CThostFtdcRspAuthenticateField", pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if pRspInfo.ErrorID != 0 and pRspInfo is not None:
            print('穿透式认证失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('穿透式认证成功！')

            # 发送登录请求
            login_field = ThostFtdcApi.CThostFtdcReqUserLoginField()
            login_field.BrokerID = self.login_info['BrokerID']
            login_field.UserID = self.login_info['UserID']
            login_field.Password = self.login_info['Password']

            ret = self.trader_user_api.ReqUserLogin(login_field, 0)
            if ret == 0:
                print('发送登录交易账户成功！')
            else:
                print('发送登录交易账户失败！')
                judge_ret(ret)


    def OnRspUserLogin(self, pRspUserLogin: "CThostFtdcRspUserLoginField", pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if pRspInfo.ErrorID != 0 and pRspInfo is not None:
            print('登录交易账户失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('登录交易账户成功！')

    def OnRspQryInstrument(self, pInstrument: "CThostFtdcInstrumentField", pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        print('OnRspQryInstrument')
        for product_id in self.sub_product_ids:
            if product_id in pInstrument.InstrumentID:
                self.exchangeId[pInstrument.InstrumentID] = pInstrument.ExchangeID
                self.expire_date[pInstrument.InstrumentID] = pInstrument.ExpireDate


