from typing import Dict
from api_se import ThostFtdcApiSOpt
from api_se.ThostFtdcApiSOpt import CThostFtdcOrderField, CThostFtdcRspAuthenticateField, CThostFtdcRspInfoField, \
    CThostFtdcInstrumentField, CThostFtdcInputOrderField, CThostFtdcTradeField, CThostFtdcSettlementInfoConfirmField, CThostFtdcInvestorPositionField, CThostFtdcInvestorPositionDetailField, CThostFtdcInputOrderActionField, THOST_FTDC_OST_Unknown, THOST_FTDC_OST_NoTradeQueueing, \
    THOST_FTDC_OST_AllTraded, THOST_FTDC_OST_Canceled, THOST_FTDC_OST_PartTradedQueueing
from utils.api import ReqQryInvestorPosition, ReqQryInvestorPositionDetail, ReqQryInstrument, ReqOrderInsert, ReqOrderAction
from utils.helper import *
from ctp.market_data_manager import MarketDataManager
from memory.user_memory_manager import UserMemoryManager
from model.instrument.instrument import Instrument
from model.instrument.option import ETFOption
from model.order_info import OrderInfo
from model.position import Position


class TraderService(ThostFtdcApiSOpt.CThostFtdcTraderSpi):
    # key: order_ref, value: order_info
    order_map: Dict[str, OrderInfo] = {}

    front_id = None
    session_id = None
    max_order_ref = 0

    trading_day = None

    market_data_manager: MarketDataManager = None


    def __init__(self, trader_user_api, config, market_data_manager: MarketDataManager, user_memory_manager: UserMemoryManager):
        super().__init__()
        self.trader_user_api = trader_user_api
        self.config = config
        self.subscribe_instrument: Dict[str, Instrument] = {}
        self.login_finish = False
        self.query_finish: Dict[str, bool] = {}
        self.market_data_manager = market_data_manager
        self.user_memory_manager = user_memory_manager

    def OnFrontConnected(self):
        print("开始建立交易连接")
        auth_field = ThostFtdcApiSOpt.CThostFtdcReqAuthenticateField()


        auth_field.BrokerID = self.config.broker_id
        auth_field.UserID = self.config.user_id
        auth_field.AppID = self.config.app_id
        auth_field.AuthCode = self.config.auth_code

        ret = self.trader_user_api.ReqAuthenticate(auth_field, 0)
        if ret == 0:
            print(f'发送穿透式认证请求成功！')
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
                # print(f"InstrumentID: {pInstrument.InstrumentID}, VolumeMultiple: {pInstrument.VolumeMultiple}")
                o = ETFOption(pInstrument.InstrumentID, pInstrument.ExpireDate, option_type, int(pInstrument.StrikePrice * 10000), pInstrument.ExchangeID, pInstrument.UnderlyingInstrID, pInstrument.VolumeMultiple / 10000)
                self.subscribe_instrument[o.id] = o

        if bIsLast:
            self.query_finish[ReqQryInstrument] = True
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
            self.query_finish[ReqQryInvestorPositionDetail] = True
            print('查询投资者持仓明细完成')

    def OnRspOrderInsert(self, pInputOrder: CThostFtdcInputOrderField, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> "void":
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('下单失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('下单成功, 风控通过')

    def OnRtnOrder(self, pOrder: CThostFtdcOrderField) -> "void":
        try:
            # 报单已提交
            if pOrder.OrderStatus == THOST_FTDC_OST_Unknown:
                print('上/深交所报单已提交')
            # 未成交
            elif pOrder.OrderStatus == THOST_FTDC_OST_NoTradeQueueing:
                print('上/深交所未成交')
            # 全部成交
            elif pOrder.OrderStatus == THOST_FTDC_OST_AllTraded:
                print('上/深交所全部成交')
                self.query_finish[ReqOrderInsert] = True
            # 撤单
            elif pOrder.OrderStatus == THOST_FTDC_OST_Canceled:
                self.query_finish[ReqOrderInsert] = True
                # 被动撤单
                if pOrder.OrderSubmitStatus == '4':
                    print('上/深交所被动撤单')
                    print(pOrder.StatusMsg)
                else:
                    print(pOrder.OrderSubmitStatus)
                    print('上/深交所撤单')
                    print(pOrder.StatusMsg)
            # 部分成交，还在队列中
            elif pOrder.OrderStatus == THOST_FTDC_OST_PartTradedQueueing:
                print('上/深交所部分成交，还在队列中')
                self.query_finish[ReqOrderInsert] = True
            else:
                print("OnRtnOrder")
                print("OrderStatus=", pOrder.OrderStatus)
                print("StatusMsg=", pOrder.StatusMsg)
        except Exception as e:
            red_print(e)

    def OnRtnTrade(self, pTrade: CThostFtdcTradeField) -> "void":
        print(f'OnRtnTrade: OrderRef {pTrade.OrderRef}')

        if pTrade.InstrumentID not in self.market_data_manager.instrument_transform_full_symbol:
            return

        full_symbol = self.market_data_manager.instrument_transform_full_symbol[pTrade.InstrumentID]
        investor_id = pTrade.InvestorID
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
        # print(f'交易成功后当前持仓:{self.user_memory_manager.print_position()}')

    def OnRspQryInvestorPosition(self, pInvestorPosition: CThostFtdcInvestorPositionField, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool) -> "void":
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('查询投资者持仓失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))

        if pInvestorPosition is not None:
            instrument_id: str = pInvestorPosition.InstrumentID
            investor_id = pInvestorPosition.InvestorID
            if instrument_id not in self.market_data_manager.instrument_transform_full_symbol:
                return

            if self.market_data_manager is None or self.user_memory_manager is None:
                return

            full_symbol = self.market_data_manager.instrument_transform_full_symbol[instrument_id]
            # print(f"OnRspQryInvestorPosition full_symbol: {full_symbol}, long: {pInvestorPosition.PosiDirection == ThostFtdcApiSOpt.THOST_FTDC_PD_Long}, position: {pInvestorPosition.Position}, today position: {pInvestorPosition.TodayPosition}")
            if full_symbol not in self.user_memory_manager.positions[investor_id]:
                self.user_memory_manager.positions[investor_id][full_symbol] = Position(instrument_id)
            if pInvestorPosition.PosiDirection == ThostFtdcApiSOpt.THOST_FTDC_PD_Long:
                self.user_memory_manager.positions[investor_id][full_symbol].long = int(pInvestorPosition.Position)
                self.user_memory_manager.positions[investor_id][full_symbol].long_open_volume = int(pInvestorPosition.OpenVolume)
                self.user_memory_manager.positions[investor_id][full_symbol].long_close_volume = int(pInvestorPosition.CloseVolume)
            elif pInvestorPosition.PosiDirection == ThostFtdcApiSOpt.THOST_FTDC_PD_Short:
                self.user_memory_manager.positions[investor_id][full_symbol].short = int(pInvestorPosition.Position)
                self.user_memory_manager.positions[investor_id][full_symbol].short_open_volume = int(pInvestorPosition.OpenVolume)
                self.user_memory_manager.positions[investor_id][full_symbol].short_close_volume = int(pInvestorPosition.CloseVolume)

        if bIsLast:
            self.query_finish[ReqQryInvestorPosition] = True
            print('查询投资者持仓完成')

    def OnRspOrderAction(self, pInputOrderAction: CThostFtdcInputOrderActionField, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool):
        if pRspInfo is not None and pRspInfo.ErrorID != 0:
            print('撤单失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))

        if bIsLast:
            self.query_finish[ReqOrderAction] = True
            print('撤单完成')











