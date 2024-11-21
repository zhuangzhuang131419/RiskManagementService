import time
from abc import ABC

from ctp.cffex.market_data_service import MarketDataService
from ctp.cffex.trader_service import TraderService
from helper.api import ReqQryInstrument, ReqQryInvestorPosition, ReqOrderInsert, ReqQryInvestorPositionDetail, ReqOrderAction
from memory.market_data_manager import MarketDataManager
from memory.user_memory_manager import UserMemoryManager
from model.config.exchange_config import ExchangeConfig
from ctp.exchange.exchange_base import Exchange
from api_cffex import ThostFtdcApi
from helper.helper import judge_ret, filter_index_future
from model.direction import Direction
from model.enum.exchange_type import ExchangeType
from model.order_info import OrderInfo


class CFFExchange(Exchange, ABC):
    def __init__(self, config: ExchangeConfig, config_file_path: str, user_memory_manager: UserMemoryManager, market_data_manager: MarketDataManager):
        super().__init__(config, config_file_path)
        self.type = ExchangeType.CFFEX
        print(f'CTP API 版本: {ThostFtdcApi.CThostFtdcTraderApi_GetApiVersion()}')
        self.user_memory_manager = user_memory_manager
        self.market_data_manager = market_data_manager

    def is_login(self):
        return True if self.trader_user_spi is not None and self.trader_user_spi.login_finish else False

    def connect_market_data(self):
        print("连接中金行情中心")
        # 创建API实例
        self.market_data_user_api = ThostFtdcApi.CThostFtdcMdApi_CreateFtdcMdApi(self.config_file_path)
        # 创建spi实例
        self.market_data_user_spi = MarketDataService(self.market_data_user_api, self.config, self.market_data_manager)
        # 连接行情前置服务器
        self.market_data_user_api.RegisterFront(self.config.market_server_front)
        # 将spi注册给api
        self.market_data_user_api.RegisterSpi(self.market_data_user_spi)
        self.market_data_user_api.Init()

    def connect_trader(self):
        print(f"连接中金交易中心")
        self.trader_user_api = ThostFtdcApi.CThostFtdcTraderApi_CreateFtdcTraderApi(self.config_file_path)
        self.trader_user_spi = TraderService(self.trader_user_api, self.config, self.market_data_manager, self.user_memory_manager)
        self.trader_user_api.RegisterSpi(self.trader_user_spi)
        self.trader_user_api.RegisterFront(self.config.trade_server_front)

        # 订阅共有流与私有流。订阅方式主要有三种，分为断点续传，重传和连接建立开始传三种。
        # TERT_RESTART：从本交易日开始重传。
        # TERT_RESUME：从上次收到的续传。
        # TERT_QUICK：只传送登录后的内容。
        self.trader_user_api.SubscribePrivateTopic(ThostFtdcApi.THOST_TERT_QUICK)
        self.trader_user_api.SubscribePublicTopic(ThostFtdcApi.THOST_TERT_QUICK)
        self.trader_user_api.Init()

    def order_action(self, instrument_id: str, order_ref: str):
        self.trader_user_spi.query_finish[ReqOrderAction] = False
        order_action_field = ThostFtdcApi.CThostFtdcInputOrderActionField()
        order_action_field.BrokerID = self.config.broker_id
        order_action_field.UserID = self.config.user_id
        order_action_field.InvestorID = self.config.investor_id
        order_action_field.FrontID = self.trader_user_spi.front_id
        order_action_field.SessionID = self.trader_user_spi.session_id
        order_action_field.InstrumentID = instrument_id
        order_action_field.ActionFlag = ThostFtdcApi.THOST_FTDC_AF_Delete
        order_action_field.OrderRef = order_ref

        ret = self.trader_user_api.ReqOrderAction(order_action_field, 0)

        if ret == 0:
            print(f'发送撤单请求成功！{order_action_field.OrderRef}')
        else:
            print('发送撤单请求失败！')
            judge_ret(ret)




    def insert_order(self, instrument_id: str, direction: Direction, limit_price: float, volume: int) -> str:
        self.trader_user_spi.query_finish[ReqOrderInsert] = False
        order_field = ThostFtdcApi.CThostFtdcInputOrderField()
        order_field.OrderRef = self.user_memory_manager.get_order_ref()
        order_field.BrokerID = self.config.broker_id
        order_field.ExchangeID = ExchangeType.CFFEX.name
        order_field.InstrumentID = instrument_id

        order_field.UserID = self.config.user_id
        order_field.InvestorID = self.config.investor_id
        order_field.LimitPrice = limit_price
        order_field.VolumeTotalOriginal = volume

        # 定义 direction 对应的方向和组合开平标志
        direction_mapping = {
            Direction.BUY_OPEN: (ThostFtdcApi.THOST_FTDC_D_Buy, '0'),
            Direction.BUY_CLOSE: (ThostFtdcApi.THOST_FTDC_D_Buy, '1'),
            Direction.SELL_OPEN: (ThostFtdcApi.THOST_FTDC_D_Sell, '0'),
            Direction.SELL_CLOSE: (ThostFtdcApi.THOST_FTDC_D_Sell, '1'),
            Direction.BUY_CLOSE_TODAY: (ThostFtdcApi.THOST_FTDC_D_Buy, ThostFtdcApi.THOST_FTDC_OF_CloseToday),
            Direction.SELL_CLOSE_TODAY: (ThostFtdcApi.THOST_FTDC_D_Sell, ThostFtdcApi.THOST_FTDC_OF_CloseToday),
        }

        # 获取方向和组合开平标志
        if direction in direction_mapping:
            order_field.Direction, order_field.CombOffsetFlag = direction_mapping[direction]
        else:
            print('下单委托类型错误！停止下单！')
            raise ValueError

        # 普通限价单默认参数
        # 报单价格条件
        order_field.OrderPriceType = ThostFtdcApi.THOST_FTDC_OPT_LimitPrice
        # 触发条件
        order_field.ContingentCondition = ThostFtdcApi.THOST_FTDC_CC_Immediately
        # 有效期类型
        order_field.TimeCondition = ThostFtdcApi.THOST_FTDC_TC_GFD
        # 成交量类型
        order_field.VolumeCondition = ThostFtdcApi.THOST_FTDC_VC_AV
        # 组合投机套保标志
        order_field.CombHedgeFlag = "1"

        # 最小成交量
        order_field.MinVolume = 0
        # 强平原因
        order_field.ForceCloseReason = ThostFtdcApi.THOST_FTDC_FCC_NotForceClose
        # 自动挂起标志
        order_field.IsAutoSuspend = 0


        ret = self.trader_user_api.ReqOrderInsert(order_field, 0)

        if ret == 0:
            print(f'发送下单{order_field.OrderRef}请求成功！')
        else:
            print('发送下单请求失败！')
            judge_ret(ret)
        return order_field.OrderRef

    # 查询合约
    def query_instrument(self):
        self.trader_user_spi.query_finish[ReqQryInstrument] = False
        query_file = ThostFtdcApi.CThostFtdcQryInstrumentField()
        query_file.ExchangeID = self.type.name
        ret = self.trader_user_api.ReqQryInstrument(query_file, 0)
        if ret == 0:
            print('发送查询合约成功！')
        else:
            print('发送查询合约失败！')
            judge_ret(ret)
            while ret != 0:
                query_file = ThostFtdcApi.CThostFtdcQryInstrumentField()
                ret = self.trader_user_api.ReqQryInstrument(query_file, 0)
                print('正在查询合约...')
                time.sleep(5)
        time.sleep(1)

    def subscribe_market_data(self, instrument_ids):
        ret = self.market_data_user_api.SubscribeMarketData(instrument_ids)
        if ret == 0:
            pass
        else:
            print('发送订阅{}合约请求失败！'.format(str(instrument_ids)))
            judge_ret(ret)
            while ret != 0:
                ret = self.market_data_user_api.mduserapi.SubscribeMarketData(instrument_ids)
                print('正在订阅{}行情...'.format(str(instrument_ids)))


    def query_investor_position(self, instrument_id):
        self.trader_user_spi.query_finish[ReqQryInvestorPosition] = False
        query_file = ThostFtdcApi.CThostFtdcQryInvestorPositionField()
        if instrument_id is not None:
            query_file.InstrumentID = instrument_id
        ret = self.trader_user_api.ReqQryInvestorPosition(query_file, 0)
        if ret == 0:
            print('发送查询持仓成功！')
        else:
            print('发送查询持仓失败！')
            judge_ret(ret)
            while ret != 0:
                ret = self.trader_user_api.ReqQryInvestorPosition(query_file, 0)
                print('正在查询持仓...')
                time.sleep(5)

    # 查看持仓明细
    def query_investor_position_detail(self):
        self.trader_user_spi.query_finish[ReqQryInvestorPositionDetail] = False
        query_file = ThostFtdcApi.CThostFtdcQryInvestorPositionDetailField()
        # query_file.BrokerID = self.config.broker_id
        ret = self.trader_user_api.ReqQryInvestorPositionDetail(query_file, 0)
        if ret == 0:
            print('发送查询持仓明细成功！')
        else:
            print('发送查询持仓明细失败！')
            judge_ret(ret)
            while ret != 0:
                query_file = ThostFtdcApi.CThostFtdcQryInvestorPositionDetailField()
                ret = self.trader_user_api.ReqQryInvestorPositionDetail(query_file, 0)
                print('正在查询持仓明细...')
                time.sleep(5)
        time.sleep(1)

    def init_market_data(self, market_data_manager: MarketDataManager):
        subscribe_future = []
        subscribe_option = []
        for instrument_id, instrument in self.trader_user_spi.subscribe_instrument.items():
            if filter_index_future(instrument_id):
                subscribe_future.append(instrument)
            else:
                subscribe_option.append(instrument)

        market_data_manager.add_index_future(subscribe_future)
        market_data_manager.add_options(subscribe_option)

