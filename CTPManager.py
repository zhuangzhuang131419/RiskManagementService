import time

from CTP_API import ThostFtdcApi
from ConfigManager import ConfigManager
from MarketData import MarketData
from Trader import Trader
from Helper import *


class CTPManager:
    market_data_user_spi = None
    market_data_user_api = None
    trader_user_api = None
    trader_user_spi = None

    def __init__(self):


        self.config_manager = ConfigManager()
        print(f'CTP API 版本: {ThostFtdcApi.CThostFtdcTraderApi_GetApiVersion()}')
        self.sever_info = self.config_manager.get_server_info()

    def connect_to_market_data(self):
        print("连接行情中心")
        # 创建API实例
        self.market_data_user_api = ThostFtdcApi.CThostFtdcMdApi_CreateFtdcMdApi('./con_file/')
        # 创建spi实例
        self.market_data_user_spi = MarketData(self.market_data_user_api)


        # 连接行情前置服务器
        self.market_data_user_api.RegisterFront(self.sever_info['MarketServerFront'])
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
        self.trader_user_api.RegisterFront(self.sever_info['TradeServerFront'])

        # API启动，init之后就会启动一个内部线程读写，并去连CTP前置
        self.trader_user_api.Init()

        # Join函数是使得函数阻塞在这里，等待api实例创建的内部线程的结束。
        # 内部线程需要release才会释放结束
        # self.trader_user_api.Join()

    def query_instrument(self):
        print("查询合约")
        query_file = ThostFtdcApi.CThostFtdcQryInstrumentField()
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




    