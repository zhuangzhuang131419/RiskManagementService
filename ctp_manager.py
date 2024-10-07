import time
from ctypes import c_int

from api import ThostFtdcApi
from config_manager import ConfigManager
from market_data import MarketData
from model.order_info import OrderInfo
from trader import Trader
from helper.Helper import *


class CTPManager:
    market_data_user_spi = None
    market_data_user_api = None
    trader_user_api = None
    trader_user_spi = None


    order_map = dict()

    def __init__(self):


        self.login_config = ConfigManager().login_config
        print(f'CTP API 版本: {ThostFtdcApi.CThostFtdcTraderApi_GetApiVersion()}')

    def connect_to_market_data(self):
        print("连接行情中心")
        # 创建API实例
        self.market_data_user_api = ThostFtdcApi.CThostFtdcMdApi_CreateFtdcMdApi('./con_file/')
        # 创建spi实例
        self.market_data_user_spi = MarketData(self.market_data_user_api)


        # 连接行情前置服务器
        self.market_data_user_api.RegisterFront(self.login_config.market_server_front)
        # 将spi注册给api
        self.market_data_user_api.RegisterSpi(self.market_data_user_spi)
        # 第5步，API正式启动，dll底层会自动去连上面注册的地址
        self.market_data_user_api.Init()
        # join的目的是为了阻塞主线程
        # self.market_data_user_api.Join()

    def connect_to_trader(self):
        print("连接交易中心")
        # 创建API实例
        self.trader_user_api = ThostFtdcApi.CThostFtdcTraderApi_CreateFtdcTraderApi('./con_file/')
        # 创建spi实例
        self.trader_user_spi = Trader(self.trader_user_api)

        self.trader_user_api.RegisterSpi(self.trader_user_spi)

        # 订阅共有流与私有流。订阅方式主要有三种，分为断点续传，重传和连接建立开始传三种。
        # TERT_RESTART：从本交易日开始重传。
        # TERT_RESUME：从上次收到的续传。
        # TERT_QUICK：只传送登录后的内容。
        self.trader_user_api.SubscribePrivateTopic(ThostFtdcApi.THOST_TERT_QUICK)
        self.trader_user_api.SubscribePublicTopic(ThostFtdcApi.THOST_TERT_QUICK)

        # 注册前置地址，是指将CTP前置的IP地址注册进API实例内
        self.trader_user_api.RegisterFront(self.login_config.trade_server_front)

        # API启动，init之后就会启动一个内部线程读写，并去连CTP前置
        self.trader_user_api.Init()

        # Join函数是使得函数阻塞在这里，等待api实例创建的内部线程的结束。
        # 内部线程需要release才会释放结束
        # self.trader_user_api.Join()

    # 查询合约
    def query_instrument(self):
        query_file = ThostFtdcApi.CThostFtdcQryInstrumentField()
        query_file.ExchangeID = "CFFEX"
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

    # 下单
    def insert_order(self, code: str, direction, price, volume, strategy_id=0):
        print('insert order')
        order_field = ThostFtdcApi.CThostFtdcInputOrderField()
        order_field.BrokerID = self.login_config.broker_id

        order_field.ExchangeID = self.trader_user_spi.exchangeId[code]
        order_field.InstrumentID = code
        order_field.UserID = self.login_config.user_id
        order_field.InvestorID = self.login_config.investor_id
        order_field.LimitPrice = price
        order_field.VolumeTotalOriginal = volume

        # 定义 direction 对应的方向和组合开平标志
        direction_mapping = {
            'buyopen': (ThostFtdcApi.THOST_FTDC_D_Buy, '0'),
            'buyclose': (ThostFtdcApi.THOST_FTDC_D_Buy, '1'),
            'sellopen': (ThostFtdcApi.THOST_FTDC_D_Sell, '0'),
            'sellclose': (ThostFtdcApi.THOST_FTDC_D_Sell, '1'),
            'buyclosetoday': (ThostFtdcApi.THOST_FTDC_D_Buy, ThostFtdcApi.THOST_FTDC_OF_CloseToday),
            'sellclosetoday': (ThostFtdcApi.THOST_FTDC_D_Sell, ThostFtdcApi.THOST_FTDC_OF_CloseToday),
        }

        # 获取方向和组合开平标志
        if direction in direction_mapping:
            order_field.Direction, order_field.CombOffsetFlag = direction_mapping[direction]
        else:
            print('下单委托类型错误！停止下单！')
            return -9


        order_ref = self.trader_user_spi.max_order_ref
        self.trader_user_spi.max_order_ref += 1
        order_field.OrderRef = str(order_ref)

        # 普通限价单的默认参数
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
        # GTD日期
        order_field.GTDDate = ""

        # 最小成交量
        order_field.MinVolume = 0
        # 强平原因
        order_field.ForceCloseReason = ThostFtdcApi.THOST_FTDC_FCC_NotForceClose
        # 自动挂起标志
        order_field.IsAutoSuspend = 0


        ret = self.trader_user_api.ReqOrderInsert(order_field, 0)

        if ret == 0:
            print('下单成功！')
            self.order_map[str(order_ref)] = OrderInfo(order_ref, strategy_id, self.trader_user_spi.front_id, self.trader_user_spi.session_id)
            # 报单回报里的报单价格和品种数据不对，所以自己记录数据
            self.order_map[str(order_ref)].orderPrice = price
            self.order_map[str(order_ref)].instrumentID = code
            # print(g.order_map)
        else:
            print('下单失败！')
            judge_ret(ret)
        return ret, order_ref


    # 查看持仓明细
    def query_investor_position_detail(self):
        query_file = self.trader_user_api.CThostFtdcQryInvestorPositionDetailField()
        query_file.BrokerID = self.login_config.broker_id
        ret = self.trader_user_api.ReqQryInvestorPositionDetail(query_file, 0)
        if ret == 0:
            print('发送查询持仓明细成功！')
        else:
            print('发送查询持仓明细失败！')
            judge_ret(ret)
            while ret != 0:
                query_file = self.trader_user_api.CThostFtdcQryInvestorPositionDetailField()
                ret = self.trader_user_api.ReqQryInvestorPositionDetail(query_file, 0)
                print('正在查询持仓明细...')
                time.sleep(5)
        time.sleep(1)

#
    def subscribe_market_data_in_batches(self, instrument_ids):
        print('开始订阅行情')

        page_size = 100
        for i in range(0, len(instrument_ids), page_size):
            page = instrument_ids[i:i + page_size]  # 获取当前分页
            self.subscribe_market_data(page)  # 处理当前分页的订阅

        print('已发送全部订阅请求')

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
                time.sleep(1)

    #
    #
    # def query_investor_position:







    