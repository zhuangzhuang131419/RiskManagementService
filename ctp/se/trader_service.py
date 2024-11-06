import copy

from click import option
from typing import Dict
from api_se import ThostFtdcApiSOpt
from api_se.ThostFtdcApiSOpt import CThostFtdcOrderField, CThostFtdcRspAuthenticateField, CThostFtdcRspInfoField, \
    CThostFtdcInstrumentField, CThostFtdcInputOrderField, CThostFtdcTradeField, CThostFtdcSettlementInfoConfirmField, CThostFtdcInvestorPositionField, CThostFtdcInvestorPositionDetailField
from helper.helper import *
from memory.memory_manager import MemoryManager
from model.instrument.instrument import Instrument
from model.instrument.option import Option, ETFOption
from model.order_info import OrderInfo
from model.position import Position


class TraderService(ThostFtdcApiSOpt.CThostFtdcTraderSpi):
    # key: order_ref, value: order_info
    order_map: Dict[str, OrderInfo] = {}

    front_id = None
    session_id = None
    max_order_ref = 0

    trading_day = None

    memory_manager: MemoryManager = None


    def __init__(self, trader_user_api, config):
        super().__init__()
        self.trader_user_api = trader_user_api
        self.config = config
        self.subscribe_instrument: Dict[str, Instrument] = {}
        self.login_finish = False
        self.query_finish: Dict[str, bool] = {}


    def set_memory_manager(self, memory_manager):
        self.memory_manager = memory_manager


    def OnFrontConnected(self):
        print("开始建立交易连接")
        auth_field = ThostFtdcApiSOpt.CThostFtdcReqAuthenticateField()


        auth_field.BrokerID = self.config.broker_id
        auth_field.UserID = self.config.user_id
        auth_field.Password = self.config.password
        auth_field.AuthCode = self.config.auth_code

        ret = self.trader_user_api.ReqAuthenticate(auth_field, 0)
        if ret == 0:
            print('发送穿透式认证请求成功！')
        else:
            print('发送穿透式认证请求失败！')
            judge_ret(ret)

    def OnRspAuthenticate(self, pRspAuthenticateField: CThostFtdcRspAuthenticateField, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> "void":
        if pRspInfo.ErrorID != 0 and pRspInfo is not None:
            print('穿透式认证失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('穿透式认证成功！')

            # 发送登录请求
            login_field = ThostFtdcApiSOpt.CThostFtdcReqUserLoginField()
            login_field.BrokerID = self.config.broker_id
            login_field.UserID = self.config.user_id
            login_field.Password = self.config.password

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

            pSettlementInfoConfirm = ThostFtdcApiSOpt.CThostFtdcSettlementInfoConfirmField()
            pSettlementInfoConfirm.BrokerID = self.config.broker_id
            pSettlementInfoConfirm.InvestorID = self.config.investor_id
            ret = self.trader_user_api.ReqSettlementInfoConfirm(pSettlementInfoConfirm, 0)
            if ret == 0:
                print('发送结算单确认请求成功！')
            else:
                print('发送结算单确认请求失败！')
                judge_ret(ret)

    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm: CThostFtdcSettlementInfoConfirmField, pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('结算单确认失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('结算单确认成功！')
            self.login_finish = True



    # 请求查询合约响应，当执行ReqQryInstrument后，该方法被调用。
    # https://documentation.help/CTP-API-cn/ONRSPQRYINSTRUMENT.html
    def OnRspQryInstrument(self, pInstrument: CThostFtdcInstrumentField, pRspInfo: CThostFtdcRspInfoField, nRequestID: "int", bIsLast: "bool") -> "void":
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('请求查询合约失败\nf错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))

        if pInstrument is not None:
            # InstrumentID: 10008312, ExchangeID: SSE, ExpiredData: 20250625, underlyinfInstrID: 510500
            if filter_etf_option(pInstrument.UnderlyingInstrID) and len(pInstrument.InstrumentID) == 8:

                # if pInstrument.UnderlyingInstrID == "510050" and pInstrument.ExpireDate == "20241225" and str(pInstrument.StrikePrice) == "2.25":
                #     print(f'InstrumentID = {pInstrument.InstrumentID}, OptionsType = {pInstrument.OptionsType}, StrikePrice = {pInstrument.StrikePrice} ')
                option_type = 'C' if int(pInstrument.OptionsType) == 1 else 'P'
                o = ETFOption(pInstrument.InstrumentID, pInstrument.ExpireDate, option_type, pInstrument.StrikePrice, pInstrument.ExchangeID, pInstrument.UnderlyingInstrID)
                self.subscribe_instrument[o.id] = o

        if bIsLast:
            self.query_finish['ReqQryInstrument'] = True
            print('查询合约完成')


    # 请求查询投资者持仓明细响应，当执行ReqQryInvestorPositionDetail后，该方法被调用。
    # https://documentation.help/CTP-API-cn/ONRSPQRYINVESTORPOSITIONDETAIL.html
    def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail: CThostFtdcInvestorPositionDetailField, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> "void":
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('查询投资者持仓明细失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('查询投资者持仓明细成功,')

        # print(f"投资者：{pInvestorPositionDetail.InvestorID} instrument: {pInvestorPositionDetail.InstrumentID} exchange_id: {pInvestorPositionDetail.ExchangeID} open price: {pInvestorPositionDetail.OpenPrice} ")
        print_struct_fields(pInvestorPositionDetail)


        if bIsLast:
            self.query_finish['RspQryInvestorPositionDetail'] = True
            print('查询投资者持仓明细完成')

    def OnRspOrderInsert(self, pInputOrder: CThostFtdcInputOrderField, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> "void":
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('下单失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('下单成功, 风控通过')

    def OnRtnOrder(self, pOrder: CThostFtdcOrderField) -> "void":
        try:
            # 报单已提交
            if pOrder.OrderStatus == 'a':
                print('报单已提交')
                self.order_map[pOrder.OrderRef].pOrder = copy.copy(pOrder)
            # 未成交
            elif pOrder.OrderStatus == '3':
                # print(pOrder.StatusMsg)
                print('未成交')
            # 全部成交
            elif pOrder.OrderStatus == '0':
                # print(pOrder.StatusMsg)
                print('全部成交')
            # 撤单
            elif pOrder.OrderStatus == '5':
                # print(pOrder.OrderStatus)
                # 被动撤单
                if pOrder.OrderSubmitStatus == '4':
                    print('被动撤单')
                    print(pOrder.StatusMsg)
                else:
                    print(pOrder.OrderSubmitStatus)
                    print('撤单')
                    print(pOrder.StatusMsg)
            # 部分成交，还在队列中
            elif pOrder.OrderStatus == '1':
                print(pOrder.OrderStatus)
                print('部分成交，还在队列中')
            else:
                print("OnRtnOrder")
                print("OrderStatus=", pOrder.OrderStatus)
                print("StatusMsg=", pOrder.StatusMsg)
        except Exception as e:
            red_print(e)

    def OnRtnTrade(self, pTrade: CThostFtdcTradeField) -> "void":
        del self.order_map[pTrade.OrderRef]

    def OnRspQryInvestorPosition(self, pInvestorPosition: CThostFtdcInvestorPositionField, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> "void":
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('查询投资者持仓失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))

        instrument_id: str = pInvestorPosition.InstrumentID
        print(f"OnRspQryInvestorPosition: {instrument_id}")

        if self.memory_manager is not None:
            symbol, option_type, strike_price = self.memory_manager.transform_instrument_id(instrument_id)

            if self.memory_manager is not None:
                symbol, option_type, strike_price = self.memory_manager.transform_instrument_id(instrument_id)
                if pInvestorPosition.PosiDirection == ThostFtdcApiSOpt.THOST_FTDC_PD_Long:
                    self.memory_manager.option_series_dict[symbol].strike_price_options[strike_price].set_position(option_type, pInvestorPosition.Position, True)
                elif pInvestorPosition.PosiDirection == ThostFtdcApiSOpt.THOST_FTDC_PD_Short:
                    self.memory_manager.option_series_dict[symbol].strike_price_options[strike_price].set_position(option_type, pInvestorPosition.Position, False)
        if bIsLast:
            self.query_finish['RspQryInvestorPositionDetail'] = True
            print('查询投资者持仓完成')








