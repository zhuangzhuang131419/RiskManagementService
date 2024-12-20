import copy
from typing import Dict

from api_cffex import ThostFtdcApi
from api_cffex.ThostFtdcApi import CThostFtdcRspInfoField, CThostFtdcRspUserLoginField, \
    CThostFtdcInstrumentField, CThostFtdcTradeField, CThostFtdcInvestorPositionField, \
    CThostFtdcInvestorPositionDetailField, CThostFtdcOrderField, CThostFtdcInputOrderField, \
    CThostFtdcRspAuthenticateField, CThostFtdcSettlementInfoConfirmField, THOST_FTDC_OST_Unknown, \
    THOST_FTDC_OST_NoTradeQueueing, THOST_FTDC_OST_Canceled, THOST_FTDC_OST_AllTraded, \
    THOST_FTDC_OST_PartTradedQueueing, CThostFtdcInputOrderActionField
from helper.api import ReqQryInvestorPosition, ReqQryInvestorPositionDetail, RspOrderInsert, ReqOrderInsert, ReqOrderAction
from helper.helper import *
from memory.market_data_manager import MarketDataManager
from memory.user_memory_manager import UserMemoryManager
from model.config.exchange_config import ExchangeConfig
from model.enum.exchange_type import ExchangeType
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
            if pOrder.OrderStatus == THOST_FTDC_OST_Unknown:
                print('中金报单已提交')
            # 未成交
            elif pOrder.OrderStatus == THOST_FTDC_OST_NoTradeQueueing:
                print('中金未成交')
            # 全部成交
            elif pOrder.OrderStatus == THOST_FTDC_OST_AllTraded:
                print('中金全部成交')
                self.query_finish[ReqOrderInsert] = True
            # 撤单
            elif pOrder.OrderStatus == THOST_FTDC_OST_Canceled:
                self.query_finish[ReqOrderInsert] = True
                # 被动撤单
                if pOrder.OrderSubmitStatus == '4':
                    print('中金被动撤单')
                    print(pOrder.StatusMsg)
                else:
                    self.query_finish[ReqOrderAction] = True
                    print('撤单完成')
                    print(pOrder.StatusMsg)
            # 部分成交，还在队列中
            elif pOrder.OrderStatus == THOST_FTDC_OST_PartTradedQueueing:
                print('中金部分成交，还在队列中')
                self.query_finish[ReqOrderInsert] = True
            else:
                print("OnRtnOrder")
                print("OrderStatus=", pOrder.OrderStatus)
                print("StatusMsg=", pOrder.StatusMsg)
        except Exception as e:
            red_print(e)

    def OnRtnTrade(self, pTrade: CThostFtdcTradeField) -> "void":
        investor_id = pTrade.InvestorID
        full_symbol = self.market_data_manager.instrument_transform_full_symbol[pTrade.InstrumentID]
        if full_symbol not in self.user_memory_manager.positions[investor_id]:
            self.user_memory_manager.positions[investor_id][full_symbol] = Position(pTrade.InstrumentID)

        if pTrade.Direction == "0":
            if pTrade.OffsetFlag == '0':
                # 买开仓
                self.user_memory_manager.positions[investor_id][full_symbol].long += int(pTrade.Volume)
                self.user_memory_manager.positions[investor_id][full_symbol].long_open_volume += int(pTrade.Volume)
            elif pTrade.OffsetFlag == '1':
                # 买平仓
                self.user_memory_manager.positions[investor_id][full_symbol].short -= int(pTrade.Volume)
                self.user_memory_manager.positions[investor_id][full_symbol].long_close_volume += int(pTrade.Volume)
        elif pTrade.Direction == "1":
            if pTrade.OffsetFlag == '0':
                # 卖开仓
                self.user_memory_manager.positions[investor_id][full_symbol].short += int(pTrade.Volume)
                self.user_memory_manager.positions[investor_id][full_symbol].short_open_volume += int(pTrade.Volume)
            elif pTrade.OffsetFlag == '1':
                # 卖平仓
                self.user_memory_manager.positions[investor_id][full_symbol].long -= int(pTrade.Volume)
                self.user_memory_manager.positions[investor_id][full_symbol].short_close_volume += int(pTrade.Volume)
        print(f'交易成功后当前持仓:{self.user_memory_manager.print_position()}')

    def OnRspQryInvestorPosition(self, pInvestorPosition: CThostFtdcInvestorPositionField, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> "void":
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('查询投资者持仓失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))

        if pInvestorPosition is not None:
            instrument_id: str = pInvestorPosition.InstrumentID
            investor_id = pInvestorPosition.InvestorID

            if instrument_id not in self.market_data_manager.instrument_transform_full_symbol:
                return

            full_symbol = self.market_data_manager.instrument_transform_full_symbol[instrument_id]
            print(f"OnRspQryInvestorPosition investor: {investor_id} instrument: {instrument_id}, long: {pInvestorPosition.PosiDirection == ThostFtdcApi.THOST_FTDC_PD_Long}, position: {pInvestorPosition.Position}, open volume: {pInvestorPosition.OpenVolume}")
            if full_symbol not in self.user_memory_manager.positions[investor_id]:
                self.user_memory_manager.positions[investor_id][full_symbol] = Position(instrument_id)
            if pInvestorPosition.PosiDirection == ThostFtdcApi.THOST_FTDC_PD_Long:
                self.user_memory_manager.positions[investor_id][full_symbol].long = int(pInvestorPosition.Position)
                self.user_memory_manager.positions[investor_id][full_symbol].long_open_volume = int(pInvestorPosition.OpenVolume)
                self.user_memory_manager.positions[investor_id][full_symbol].long_close_volume = int(pInvestorPosition.CloseVolume)
            elif pInvestorPosition.PosiDirection == ThostFtdcApi.THOST_FTDC_PD_Short:
                self.user_memory_manager.positions[investor_id][full_symbol].short = int(pInvestorPosition.Position)
                self.user_memory_manager.positions[investor_id][full_symbol].short_open_volume = int(pInvestorPosition.OpenVolume)
                self.user_memory_manager.positions[investor_id][full_symbol].short_close_volume = int(pInvestorPosition.CloseVolume)

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
            self.query_finish[ReqQryInvestorPositionDetail] = True
            print('查询投资者持仓明细完成')

    def OnRspOrderAction(self, pInputOrderAction: CThostFtdcInputOrderActionField, pRspInfo: "CThostFtdcRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('撤单失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))

        print('OnRspOrderAction')

        if bIsLast:
            self.query_finish[ReqOrderAction] = True
            print('撤单完成')











