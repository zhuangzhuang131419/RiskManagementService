from api import ThostFtdcApi
from api.ThostFtdcApi import CThostFtdcRspInfoField, CThostFtdcRspUserLoginField, \
    CThostFtdcInstrumentField
from config_manager import ConfigManager
from helper.Helper import *

class Trader(ThostFtdcApi.CThostFtdcTraderSpi):
    # 指数期货的品种列表
    Index_Future_ProductIDlist = ['IH', 'IF', 'IM']
    # 指数期权的品种列表
    Index_Option_ProductIDlist = ['HO', 'IO', 'MO']

    sub_product_ids = Index_Future_ProductIDlist + Index_Option_ProductIDlist
    exchange_id = dict()
    expire_date = dict()

    front_id = None
    session_id = None
    max_order_ref = 0

    trading_day = None

    # flag
    login_finish = False
    query_finish = False


    def __init__(self, trader_user_api):
        super().__init__()
        self.trader_user_api = trader_user_api
        self.login_info = ConfigManager().login_config


    def OnFrontConnected(self):
        print("开始建立交易连接")
        auth_field = ThostFtdcApi.CThostFtdcReqAuthenticateField()


        auth_field.BrokerID = self.login_info.broker_id
        auth_field.UserID = self.login_info.user_id
        auth_field.Password = self.login_info.password
        auth_field.AuthCode = self.login_info.auth_code

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
            login_field.BrokerID = self.login_info.broker_id
            login_field.UserID = self.login_info.user_id
            login_field.Password = self.login_info.password

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

            # 保存数据用于下单
            self.front_id = pRspUserLogin.FrontID
            self.session_id = pRspUserLogin.SessionID
            self.max_order_ref = int(pRspUserLogin.MaxOrderRef)

            # 保存交易日
            self.trading_day = pRspUserLogin.TradingDay

            pSettlementInfoConfirm = ThostFtdcApi.CThostFtdcSettlementInfoConfirmField()
            pSettlementInfoConfirm.BrokerID = self.login_info.broker_id
            pSettlementInfoConfirm.InvestorID = self.login_info.investor_id
            ret = self.trader_user_api.ReqSettlementInfoConfirm(pSettlementInfoConfirm, 0)
            if ret == 0:
                print('发送结算单确认请求成功！')
            else:
                print('发送结算单确认请求失败！')
                judge_ret(ret)

    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm: "CThostFtdcSettlementInfoConfirmField", pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if pRspInfo.ErrorID != 0 and pRspInfo is not None:
            print('结算单确认失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('结算单确认成功！')
            self.login_finish = True



    # 请求查询合约响应，当执行ReqQryInstrument后，该方法被调用。
    # https://documentation.help/CTP-API-cn/ONRSPQRYINSTRUMENT.html
    def OnRspQryInstrument(self, pInstrument: "CThostFtdcInstrumentField", pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        for product_id in self.sub_product_ids:
            if product_id in pInstrument.InstrumentID:
                self.exchange_id[pInstrument.InstrumentID] = pInstrument.ExchangeID
                self.expire_date[pInstrument.InstrumentID] = pInstrument.ExpireDate

        if bIsLast:
            self.query_finish = True
            print('查询合约完成')


    # 请求查询投资者持仓明细响应，当执行ReqQryInvestorPositionDetail后，该方法被调用。
    # https://documentation.help/CTP-API-cn/ONRSPQRYINVESTORPOSITIONDETAIL.html
    def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail: "CThostFtdcInvestorPositionDetailField", pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if pInvestorPositionDetail.Volume == 0:
            return



