import time
from abc import ABC
from uuid import uuid4

from ctp.se.market_data_service import MarketDataService
from ctp.se.trader_service import TraderService
from memory.memory_manager import MemoryManager
from model.exchange.exchange_base import Exchange
from api_se import ThostFtdcApiSOpt
from helper.helper import judge_ret
from model.direction import Direction
from model.order_info import OrderInfo


class SExchange(Exchange, ABC):
    def __init__(self, config, config_file_path, memory_manager: MemoryManager):
        super().__init__(config, config_file_path)
        print(f'CTP API 版本: {ThostFtdcApiSOpt.CThostFtdcTraderApi_GetApiVersion()}')
        self.memory: MemoryManager = memory_manager

    def connect_market_data(self):
        print(f"连接深交行情中心")
        # 创建API实例
        self.market_data_user_api = ThostFtdcApiSOpt.CThostFtdcMdApi_CreateFtdcMdApi(self.config_file_path)
        # 创建spi实例
        self.market_data_user_spi = MarketDataService(self.market_data_user_api, self.config)
        # 连接行情前置服务器
        self.market_data_user_api.RegisterFront(self.config.market_server_front)
        # 将spi注册给api
        self.market_data_user_api.RegisterSpi(self.market_data_user_spi)
        self.market_data_user_api.Init()

    def connect_trader(self):
        print(f"连接深交交易中心")
        self.trader_user_api = ThostFtdcApiSOpt.CThostFtdcTraderApi_CreateFtdcTraderApi(self.config_file_path)
        self.trader_user_spi = TraderService(self.trader_user_api, self.config)

        self.trader_user_api.RegisterSpi(self.trader_user_spi)
        self.trader_user_api.RegisterFront(self.config.trade_server_front)

        # 订阅共有流与私有流。订阅方式主要有三种，分为断点续传，重传和连接建立开始传三种。
        # TERT_RESTART：从本交易日开始重传。
        # TERT_RESUME：从上次收到的续传。
        # TERT_QUICK：只传送登录后的内容。
        self.trader_user_api.SubscribePrivateTopic(ThostFtdcApiSOpt.THOST_TERT_QUICK)
        self.trader_user_api.SubscribePublicTopic(ThostFtdcApiSOpt.THOST_TERT_QUICK)
        self.trader_user_api.Init()

    def query_instrument(self):
        self.trader_user_spi.query_finish['ReqQryInstrument'] = False
        query_file = ThostFtdcApiSOpt.CThostFtdcQryInstrumentField()
        ret = self.trader_user_api.ReqQryInstrument(query_file, 0)
        if ret == 0:
            print('发送查询合约成功！')
        else:
            print('发送查询合约失败！')
            judge_ret(ret)
            while ret != 0:
                query_file = ThostFtdcApiSOpt.CThostFtdcQryInstrumentField()
                ret = self.trader_user_api.ReqQryInstrument(query_file, 0)
                print('正在查询合约...')
                time.sleep(5)
        time.sleep(1)

    def insert_order(self, instrument_id: str, direction: Direction, limit_price: float, volume: int):
        order_field = ThostFtdcApiSOpt.CThostFtdcInputOrderField()
        order_field.OrderRef = self.memory.get_order_ref()
        order_field.BrokerID = self.config.broker_id

        # order_field.ExchangeID = self.trader_user_spi.exchange_id[code]
        order_field.InstrumentID = instrument_id
        order_field.UserID = self.config.user_id
        order_field.InvestorID = self.config.investor_id
        order_field.LimitPrice = limit_price
        order_field.VolumeTotalOriginal = volume

        # 定义 direction 对应的方向和组合开平标志
        direction_mapping = {
            Direction.BUY_OPEN: (ThostFtdcApiSOpt.THOST_FTDC_D_Buy, '0'),
            Direction.BUY_CLOSE: (ThostFtdcApiSOpt.THOST_FTDC_D_Buy, '1'),
            Direction.SELL_OPEN: (ThostFtdcApiSOpt.THOST_FTDC_D_Sell, '0'),
            Direction.SELL_CLOSE: (ThostFtdcApiSOpt.THOST_FTDC_D_Sell, '1'),
            Direction.BUY_CLOSE_TODAY: (ThostFtdcApiSOpt.THOST_FTDC_D_Buy, ThostFtdcApiSOpt.THOST_FTDC_OF_CloseToday),
            Direction.SELL_CLOSE_TODAY: (ThostFtdcApiSOpt.THOST_FTDC_D_Sell, ThostFtdcApiSOpt.THOST_FTDC_OF_CloseToday),
        }



        # 获取方向和组合开平标志
        if direction in direction_mapping:
            order_field.Direction, order_field.CombOffsetFlag = direction_mapping[direction]
        else:
            print('下单委托类型错误！停止下单！')
            return -9

        # 普通限价单默认参数
        # 报单价格条件
        order_field.OrderPriceType = ThostFtdcApiSOpt.THOST_FTDC_OPT_LimitPrice
        # 触发条件
        order_field.ContingentCondition = ThostFtdcApiSOpt.THOST_FTDC_CC_Immediately
        # 有效期类型
        order_field.TimeCondition = ThostFtdcApiSOpt.THOST_FTDC_TC_GFD
        # 成交量类型
        order_field.VolumeCondition = ThostFtdcApiSOpt.THOST_FTDC_VC_AV
        # 组合投机套保标志
        order_field.CombHedgeFlag = "1"
        # GTD日期
        order_field.GTDDate = ""

        # 最小成交量
        order_field.MinVolume = 0
        # 强平原因
        order_field.ForceCloseReason = ThostFtdcApiSOpt.THOST_FTDC_FCC_NotForceClose
        # 自动挂起标志
        order_field.IsAutoSuspend = 0


        ret = self.trader_user_api.ReqOrderInsert(order_field, 0)

        if ret == 0:
            print('发送下单请求成功！')
            self.trader_user_spi.order_map[order_field.OrderRef] = OrderInfo(order_field.OrderRef, self.trader_user_spi.front_id, self.trader_user_spi.session_id)
            # 报单回报里的报单价格和品种数据不对，所以自己记录数据
            self.trader_user_spi.order_map[order_field.OrderRef].order_price = limit_price
            self.trader_user_spi.order_map[order_field.OrderRef].instrument_id = instrument_id
            print(self.trader_user_spi.order_map[order_field.OrderRef])
        else:
            print('发送下单请求失败！')
            judge_ret(ret)
        return ret, order_field.OrderRef


    # 查看持仓明细
    def query_investor_position_detail(self):
        query_file = ThostFtdcApiSOpt.CThostFtdcQryInvestorPositionDetailField()
        # query_file.BrokerID = self.config.broker_id
        ret = self.trader_user_api.ReqQryInvestorPositionDetail(query_file, 0)
        if ret == 0:
            print('发送查询持仓明细成功！')
        else:
            print('发送查询持仓明细失败！')
            judge_ret(ret)
            while ret != 0:
                query_file = ThostFtdcApiSOpt.CThostFtdcQryInvestorPositionDetailField()
                ret = self.trader_user_api.ReqQryInvestorPositionDetail(query_file, 0)
                print('正在查询持仓明细...')
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
        self.trader_user_spi.query_finish['ReqQryInvestorPosition'] = False
        query_file = ThostFtdcApiSOpt.CThostFtdcQryInvestorPositionField()
        if instrument_id is not None:
            query_file.InstrumentID = instrument_id
        ret = self.trader_user_api.ReqQryInvestorPosition(query_file, 0)
        if ret == 0:
            pass
        else:
            print(f"发送查询投资者持仓请求失败")
            judge_ret(ret)

    def init_memory(self):
        self.memory.init_se_instrument(self.trader_user_spi.subscribe_instrument)
        self.trader_user_spi.set_memory_manager(self.memory)
        self.market_data_user_spi.set_memory_manager(self.memory)