from CTP_API import ThostFtdcApi as api
from ConfigManager import ConfigManager
from MarketData import MarketData


class CTPManager:
    def __init__(self):
        self.market_data_user_spi = None
        self.market_data_user_api = None
        self.config_manager = ConfigManager()
        print(f'CTP API 版本: {api.CThostFtdcTraderApi_GetApiVersion()}')

    def connect_to_market_data(self):
        print("连接行情中心")
        # 创建API实例
        self.market_data_user_api = api.CThostFtdcMdApi_CreateFtdcMdApi('./con_file/')
        # 创建spi实例
        self.market_data_user_spi = MarketData(self.market_data_user_api)

        sever_info = self.config_manager.get_server_info()
        # 连接行情前置服务器
        self.market_data_user_api.RegisterFront(sever_info['MarketServerFront'])
        # 将spi注册给api
        self.market_data_user_api.RegisterSpi(self.market_data_user_spi)
        # 第5步，API正式启动，dll底层会自动去连上面注册的地址
        self.market_data_user_api.Init()
        # join的目的是为了阻塞主线程
        # self.market_data_user_api.Join()

    