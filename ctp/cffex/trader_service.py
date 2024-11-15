import copy
from typing import Dict

from api_cffex import ThostFtdcApi
from api_cffex.ThostFtdcApi import CThostFtdcRspInfoField, CThostFtdcRspUserLoginField, \
    CThostFtdcInstrumentField, CThostFtdcTradeField, CThostFtdcInvestorPositionField, \
    CThostFtdcInvestorPositionDetailField, CThostFtdcOrderField, CThostFtdcInputOrderField, \
    CThostFtdcRspAuthenticateField, CThostFtdcSettlementInfoConfirmField
from helper.api import ReqQryInvestorPosition, RspQryInvestorPositionDetail, RspOrderInsert
from helper.helper import *
from memory.market_data_manager import MarketDataManager
from memory.user_memory_manager import UserMemoryManager
from model.config.exchange_config import ExchangeConfig
from model.instrument.future import Future
from model.instrument.option import IndexOption
from model.order_info import OrderInfo
from model.position import Position


class TraderService(ThostFtdcApi.CThostFtdcTraderSpi):
    # key: order_ref, value: order_info
    order_map: Dict[str, OrderInfo] = {}

    front_id = None
    session_id = None

    trading_day = None


    def __init__(self, trader_user_api, config, market_data_manager: MarketDataManager, user_memory_manager: UserMemoryManager):
        super().__init__()
        self.trader_user_api = trader_user_api
        self.config: ExchangeConfig = config
        self.subscribe_instrument = {}
        self.login_finish = False
        self.query_finish: Dict[str, bool] = {}
        self.market_data_manager = market_data_manager
        self.user_memory_manager = user_memory_manager


    def OnFrontConnected(self):
        print("开始建立交易连接")
        auth_field = ThostFtdcApi.CThostFtdcReqAuthenticateField()


        auth_field.BrokerID = self.config.broker_id
        auth_field.UserID = self.config.user_id
        auth_field.AppID = self.config.app_id
        auth_field.Password = self.config.password
        auth_field.AuthCode = self.config.auth_code

        ret = self.trader_user_api.ReqAuthenticate(auth_field, 0)
        if ret == 0:
            print('发送穿透式认证请求成功！')
        else:
            print('发送穿透式认证请求失败！')
            judge_ret(ret)

    def OnRspAuthenticate(self, pRspAuthenticateField: CThostFtdcRspAuthenticateField, pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if pRspInfo.ErrorID != 0 and pRspInfo is not None:
            print('穿透式认证失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('穿透式认证成功！')

            # 发送登录请求
            login_field = ThostFtdcApi.CThostFtdcReqUserLoginField()
            login_field.BrokerID = self.config.broker_id
            login_field.UserID = self.config.user_id
            login_field.Password = self.config.password

            ret = self.trader_user_api.ReqUserLogin(login_field, 0)
            if ret == 0:
                print('发送登录交易账户成功！')
            else:
                print('发送登录交易账户失败！')
                judge_ret(ret)


    def OnRspUserLogin(self, pRspUserLogin: CThostFtdcRspUserLoginField, pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if pRspInfo.ErrorID != 0 and pRspInfo is not None:
            print('登录交易账户失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('登录交易账户成功！')

            # 保存数据用于下单
            self.front_id = pRspUserLogin.FrontID
            self.session_id = pRspUserLogin.SessionID
            # self.max_order_ref = int(pRspUserLogin.MaxOrderRef)

            # 保存交易日
            self.trading_day = pRspUserLogin.TradingDay

            confirm_field = ThostFtdcApi.CThostFtdcSettlementInfoConfirmField()
            confirm_field.BrokerID = self.config.broker_id
            confirm_field.InvestorID = self.config.investor_id
            ret = self.trader_user_api.ReqSettlementInfoConfirm(confirm_field, 0)
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

        # print(f"InstrumentID: {pInstrument.InstrumentID}, VolumeMultiple: {pInstrument.VolumeMultiple}")

        if pInstrument is not None:
            if filter_index_option(pInstrument.InstrumentID):
                option = IndexOption(pInstrument.InstrumentID, pInstrument.ExpireDate, pInstrument.ExchangeID, pInstrument.UnderlyingMultiple)
                self.subscribe_instrument[option.id] = option
            elif filter_index_future(pInstrument.InstrumentID):
                future = Future(pInstrument.InstrumentID, pInstrument.ExpireDate, pInstrument.ExchangeID, pInstrument.UnderlyingInstrID)
                self.subscribe_instrument[future.id] = future
        if bIsLast:
            self.query_finish['ReqQryInstrument'] = True
            print('查询合约完成')




    def OnRspOrderInsert(self, pInputOrder: CThostFtdcInputOrderField, pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('下单失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('下单成功, 风控通过')

        if bIsLast:
            self.query_finish[RspOrderInsert] = True

    def OnRtnOrder(self, pOrder: CThostFtdcOrderField) -> "void":
        try:
            # 报单已提交
            if pOrder.OrderStatus == 'a':
                print('报单已提交')
                self.order_map[pOrder.OrderRef] = OrderInfo(pOrder.OrderRef, self.front_id, self.session_id)
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
        print(f'OnRtnTrade: OrderRef {pTrade.OrderRef}')
        if pTrade.OrderRef in self.order_map:
            print('delete order map')
            del self.order_map[pTrade.OrderRef]

        # 更新持仓信息
        self.user_memory_manager.refresh_position()
        self.query_finish['ReqQryInvestorPosition'] = False
        query_file = ThostFtdcApi.CThostFtdcQryInvestorPositionField()
        ret = self.trader_user_api.ReqQryInvestorPosition(query_file, 0)
        if ret == 0:
            print(f"发送查询投资者持仓请求成功")
            pass
        else:
            print(f"发送查询投资者持仓请求失败")
            judge_ret(ret)

    def OnRspQryInvestorPosition(self, pInvestorPosition: CThostFtdcInvestorPositionField, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> "void":
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('查询投资者持仓失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))

        if pInvestorPosition is not None:
            instrument_id: str = pInvestorPosition.InstrumentID
            if instrument_id in self.market_data_manager.instrument_transform_full_symbol:
                full_symbol = self.market_data_manager.instrument_transform_full_symbol[instrument_id]
                print(f"instrument: {instrument_id}, long: {pInvestorPosition.PosiDirection == ThostFtdcApi.THOST_FTDC_PD_Long}, position: {pInvestorPosition.Position}")
                self.user_memory_manager.position[full_symbol] = Position(instrument_id)
                if pInvestorPosition.PosiDirection == ThostFtdcApi.THOST_FTDC_PD_Long:
                    self.user_memory_manager.position[full_symbol].long = int(pInvestorPosition.Position)
                elif pInvestorPosition.PosiDirection == ThostFtdcApi.THOST_FTDC_PD_Short:
                    self.user_memory_manager.position[full_symbol].short = int(pInvestorPosition.Position)

        if bIsLast:
            self.query_finish[ReqQryInvestorPosition] = True
            print('查询投资者持仓完成')

    # 请求查询投资者持仓明细响应，当执行ReqQryInvestorPositionDetail后，该方法被调用。
    # https://documentation.help/CTP-API-cn/ONRSPQRYINVESTORPOSITIONDETAIL.html
    def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail: CThostFtdcInvestorPositionDetailField, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> "void":
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('查询投资者持仓明细失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))

        print(
            f"投资者：{pInvestorPositionDetail.InvestorID} instrument: {pInvestorPositionDetail.InstrumentID} exchange_id: {pInvestorPositionDetail.ExchangeID} open price: {pInvestorPositionDetail.OpenPrice}, open date: {pInvestorPositionDetail.OpenDate}, volume: {pInvestorPositionDetail.Volume}, direction: {pInvestorPositionDetail.Direction}")

        if bIsLast:
            self.query_finish[RspQryInvestorPositionDetail] = True
            print('查询投资者持仓明细完成')










