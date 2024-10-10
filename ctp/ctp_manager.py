import os.path
import time
from ctypes import c_int

from api import ThostFtdcApi
from config_manager import ConfigManager
from ctp.market_data import MarketData
from memory.memory_manager import MemoryManager
from model.direction import Direction
from model.instrument.instrument import Future
from model.instrument.option import Option
from model.order_info import OrderInfo
from ctp.trader import Trader
from helper.Helper import *
from typing import List


class CTPManager:
    # 行情中心
    market_data_user_spi = None
    market_data_user_api = None

    # 交易中心
    trader_user_api = None
    trader_user_spi = None

    # 内存中心
    memory : MemoryManager

    CONFIG_FILE_PATH = '../con_file/'


    def __init__(self):
        self.login_config = ConfigManager().login_config
        if not os.path.exists(self.CONFIG_FILE_PATH):
            os.makedirs(self.CONFIG_FILE_PATH)
        print(f'CTP API 版本: {ThostFtdcApi.CThostFtdcTraderApi_GetApiVersion()}')

    def connect_to_market_data(self):
        print("连接行情中心")
        # 创建API实例
        self.market_data_user_api = ThostFtdcApi.CThostFtdcMdApi_CreateFtdcMdApi(self.CONFIG_FILE_PATH)
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
        self.trader_user_api = ThostFtdcApi.CThostFtdcTraderApi_CreateFtdcTraderApi(self.CONFIG_FILE_PATH)
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
    def insert_order(self, code: str, direction: Direction, price, volume, strategy_id=0):
        order_field = ThostFtdcApi.CThostFtdcInputOrderField()
        order_field.BrokerID = self.login_config.broker_id

        order_field.ExchangeID = self.trader_user_spi.exchange_id[code]
        order_field.InstrumentID = code
        order_field.UserID = self.login_config.user_id
        order_field.InvestorID = self.login_config.investor_id
        order_field.LimitPrice = price
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
            return -9


        order_ref = self.trader_user_spi.max_order_ref
        self.trader_user_spi.max_order_ref += 1
        order_field.OrderRef = str(order_ref)

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
            print('发送下单请求成功！')
            self.trader_user_spi.order_map[str(order_ref)] = OrderInfo(order_ref, strategy_id, self.trader_user_spi.front_id, self.trader_user_spi.session_id)
            # 报单回报里的报单价格和品种数据不对，所以自己记录数据
            self.trader_user_spi.order_map[str(order_ref)].order_price = price
            self.trader_user_spi.order_map[str(order_ref)].instrument_id = code
            print(self.trader_user_spi.order_map[str(order_ref)])
        else:
            print('发送下单请求失败！')
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

    # 批量订阅
    def subscribe_market_data_in_batches(self, instrument_ids: List[str]):
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


    def tick(self):
        while True:
            depth_market_date = self.market_data_user_spi.market_data.get()

            # update_time = depth_market_date.UpdateTime
            # data_list = depth_market_date.InstrumentID
            # 清洗编码问题，数据分类：-1为编码错误

            if is_index_future(depth_market_date.InstrumentID) or is_index_option(depth_market_date.InstrumentID):

                market_data_list = [round(time.time()), depth_market_date.BidPrice1, depth_market_date.BidVolume1, depth_market_date.AskPrice1, depth_market_date.AskVolume1, 0]
                for i, data in enumerate(market_data_list):
                    # 遍历所有的行情字段，判断是否double最大值
                    if (isinstance(data, int) or isinstance(data, float)) and (abs(data - 1.7976931348623157e+308) < 0.000001):
                        market_data_list[i] = -1

                market_data_list = [market_data_list[0], round(market_data_list[1], 1), int(market_data_list[2]), round(market_data_list[3], 3), int(market_data_list[4]), 0]

                # 判断是否可交易
                if depth_market_date.BidVolume1 >= 1 and depth_market_date.AskVolume1 >= 1 and depth_market_date.BidPrice1 > 0 and depth_market_date.AskPrice1 > 0:
                    market_data_list[5] = 1
                else:
                    market_data_list[5] = 0

                if is_index_option(depth_market_date.InstrumentID):
                    # 导入期权行情
                    try:
                        o = Option(depth_market_date.InstrumentID, "")
                        l1 = self.memory.option_manager.index_option_month_forward_id.index(o.symbol)
                        l2 = OPTION_PUT_CALL_DICT[o.option_type]
                        l3 = self.memory.option_manager.option_series_dict[o.symbol].get_all_strike_price().index(o.strike_price)
                    except ValueError as e:
                        print(f"ValueError: {e} - Couldn't find the symbol or strike price in the list. instrument: {depth_market_date.InstrumentID}")
                    except Exception as e:
                        print(f"Exception: {e} - instrument id: {depth_market_date.InstrumentID}")
                        continue


                    self.memory.option_manager.index_option_market_data[l1, l2, l3, 1:7] = market_data_list
                elif is_index_future(depth_market_date.InstrumentID):
                    # 导入期货行情
                    f = Future(depth_market_date.InstrumentID, "")
                    try:
                        l1 = self.memory.future_manager.index_future_month_id.index(f.symbol)
                    except ValueError as e:
                        print(f"ValueError: {e} - Couldn't find the symbol in the list. future: {f}")
                        continue
                    self.memory.future_manager.index_future_market_data[l1, 0:6] = market_data_list
            else:
                # 非订阅行情
                continue



    #
    #
    # def query_investor_position:







    