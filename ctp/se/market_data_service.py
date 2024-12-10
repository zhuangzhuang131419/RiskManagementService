import copy
import time

from api_se import ThostFtdcApiSOpt
from api_se.ThostFtdcApiSOpt import CThostFtdcRspInfoField, CThostFtdcRspUserLoginField, CThostFtdcDepthMarketDataField
from helper.helper import *
from queue import Queue

from memory.market_data_manager import MarketDataManager
from model.instrument.option import Option, ETFOption
from model.memory.market_data import MarketData, DepthMarketData


class MarketDataService(ThostFtdcApiSOpt.CThostFtdcMdSpi):
    def __init__(self, market_data_user_api, config, market_data_manager: MarketDataManager):
        super().__init__()
        self.market_data_user_api = market_data_user_api
        self.config = config
        self.market_data = Queue()
        self.market_data_manager = market_data_manager

    # 当客户端与交易后台建立起通信连接时（还未登录前），该方法被调用
    def OnFrontConnected(self):
        print("开始建立行情连接")


        login_field = ThostFtdcApiSOpt.CThostFtdcReqUserLoginField()

        login_field.BrokerID = self.config.broker_id
        login_field.UserID = self.config.user_id
        login_field.Password = self.config.password

        ret = self.market_data_user_api.ReqUserLogin(login_field, 0)

        if ret == 0:
            print('发送用户登录行情账户请求成功！')
        else:
            print('发送用户登录行情账户请求失败！')
            judge_ret(ret)

    # ReqUserLogin
    def OnRspUserLogin(self, pRspUserLogin: CThostFtdcRspUserLoginField, pRspInfo: CThostFtdcRspInfoField, nRequestID: int, bIsLast: bool):
        if pRspInfo.ErrorID != 0 and pRspInfo is not None:
            print('行情连接失败\n错误信息为：{}\n错误代码为：{}'.format(pRspInfo.ErrorMsg, pRspInfo.ErrorID))
        else:
            print('行情账户登录成功！')

    # SubscribeMarketData
    def OnRspSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID != 0:
            print(f"订阅行情失败，合约: {pSpecificInstrument.InstrumentID}, 错误信息: {pRspInfo.ErrorMsg}")
        # else:
        #     if not is_index_option(pSpecificInstrument.InstrumentID) and not is_index_future(pSpecificInstrument.InstrumentID):
        #         print(f"订阅合约 {pSpecificInstrument.InstrumentID} 成功")

    # 深度行情通知
    def OnRtnDepthMarketData(self, pDepthMarketData: CThostFtdcDepthMarketDataField) -> "void":
        if self.market_data_manager is not None:
            if pDepthMarketData.InstrumentID in self.market_data_manager.instrument_transform_full_symbol:

                if pDepthMarketData.InstrumentID == "10007328":
                    print(f"ask_price: {pDepthMarketData.AskPrice1} ask_volume: {pDepthMarketData.AskVolume1} bid_price: {pDepthMarketData.BidPrice1}")
                self.market_data_manager.clock = pDepthMarketData.UpdateTime

                depth_market_data = DepthMarketData()
                depth_market_data.symbol = self.market_data_manager.instrument_transform_full_symbol[pDepthMarketData.InstrumentID]

                depth_market_data.time = round(time.time())
                depth_market_data.ask_volumes[0] = int(pDepthMarketData.AskVolume1)
                depth_market_data.bid_volumes[0] = int(pDepthMarketData.BidVolume1)
                depth_market_data.ask_prices[0] = pDepthMarketData.AskPrice1 * 10000
                depth_market_data.bid_prices[0] = pDepthMarketData.BidPrice1 * 10000

                depth_market_data.ask_volumes[1] = int(pDepthMarketData.AskVolume2)
                depth_market_data.bid_volumes[1] = int(pDepthMarketData.BidVolume2)
                depth_market_data.ask_prices[1] = pDepthMarketData.AskPrice2 * 10000
                depth_market_data.bid_prices[1] = pDepthMarketData.BidPrice2 * 10000

                depth_market_data.ask_volumes[2] = int(pDepthMarketData.AskVolume3)
                depth_market_data.bid_volumes[2] = int(pDepthMarketData.BidVolume3)
                depth_market_data.ask_prices[2] = pDepthMarketData.AskPrice3 * 10000
                depth_market_data.bid_prices[2] = pDepthMarketData.BidPrice3 * 10000

                depth_market_data.ask_volumes[3] = int(pDepthMarketData.AskVolume4)
                depth_market_data.bid_volumes[3] = int(pDepthMarketData.BidVolume4)
                depth_market_data.ask_prices[3] = pDepthMarketData.AskPrice4 * 10000
                depth_market_data.bid_prices[3] = pDepthMarketData.BidPrice4 * 10000

                depth_market_data.ask_volumes[4] = int(pDepthMarketData.AskVolume5)
                depth_market_data.bid_volumes[4] = int(pDepthMarketData.BidVolume5)
                depth_market_data.ask_prices[4] = pDepthMarketData.AskPrice5 * 10000
                depth_market_data.bid_prices[4] = pDepthMarketData.BidPrice5 * 10000

                depth_market_data.exchange_id = pDepthMarketData.ExchangeID
                depth_market_data.set_available()

                depth_market_data.clean_data()

                symbol, option_type, strike_price = parse_option_full_symbol(depth_market_data.symbol)
                if option_type == OptionType.C:
                    self.market_data_manager.option_market_data[symbol].strike_price_options[strike_price].call.market_data = depth_market_data
                elif option_type == OptionType.P:
                    self.market_data_manager.option_market_data[symbol].strike_price_options[strike_price].put.market_data = depth_market_data










