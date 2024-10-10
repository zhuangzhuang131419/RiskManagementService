import datetime
import numpy as np
from numpy.core.records import ndarray

from helper.Helper import INDEX_OPTION_PREFIXES, count_trading_days, HOLIDAYS, YEAR_TRADING_DAY
from model.instrument.option import Option
from model.instrument.option_series import OptionSeries


class OptionManager:
    # 期权链
    option_series_dict = dict()

    # 到期时间
    option_expired_date = []

    # 剩余时间
    index_option_remain_day = []

    # 期权品种月份列表
    index_option_month_forward_id = []

    # 期权品种月份行权价数量
    index_option_month_strike_num = []
    index_option_month_strike_prices = {} # ['HO2410':{2400, 2500}]

    # 最多数量的行权价
    index_option_month_strike_max_num = 0

    # 期权行情结构
    # 第一个维度：品种月份维度，顺序与期权品种月份列表对齐，[0, : , : , : ]代表HO2410
    # 第二个维度：固定大小为2，看涨or 看跌，看涨期权为0，看跌期权为1
    # 第三个维度：行权价维度
    # 第四个维度：字段维度固定大写为7，七个字段存放内容为：行权价，字段时间，bid, bidv, ask, askv, available
    # 例如要取HO2410的看涨期权的第一个行权价的bid价格，index_option_market_data[0, 0, 0, 2]
    index_option_market_data = ndarray




    index_option_month_atm_vol = ndarray

    index_option_month_model_para = ndarray

    index_option_month_t_iv = ndarray

    index_option_month_greeks = ndarray

    def __init__(self, index_options: [Option]):
        self.init_option_series(index_options)
        self.init_index_option_month_id()
        self.init_index_option_expired_date(index_options)
        self.init_index_option_remain_day()
        self.init_index_option_month_strike_num()
        self.init_index_option_market_data()

        #初始化IS相关数组
        self.index_option_month_forward_price = None
        self.init_index_option_month_forward_price()

        self.init_index_option_month_atm_vol()
        self.init_index_option_month_model_para()

        #初始化T型IV相关结构
        self.init_index_option_month_t_iv()
        self.init_index_option_month_greeks()

    def init_option_series(self, options: [Option]):
        """
        根据期权名称分组期权并初始化 OptionSeries。
        :param options: List[Option] - Option 对象的列表
        """
        option_series_dict = {}

        # 按名称分组期权
        for option in options:
            if option.symbol not in option_series_dict:
                option_series_dict[option.symbol] = []
            option_series_dict[option.symbol].append(option)

        # 初始化 OptionSeries
        for name, options_list in option_series_dict.items():
            self.option_series_dict[name] = OptionSeries(name, options_list)



    def init_index_option_month_id(self):
        """
        生成唯一的期权月份列表，格式如：["HO2410","HO2411","HO2412","HO2501","HO2503","HO2506",…,…]
        """

        for name in self.option_series_dict.keys():
            self.index_option_month_forward_id.append(name)

        sorted(self.index_option_month_forward_id)

    def init_index_option_expired_date(self, options: [Option]):
        expired_date = set()
        for option in options:
            expired_date.add(option.expired_date)

        expired_date_list = sorted(list(expired_date))
        for _ in INDEX_OPTION_PREFIXES:
            self.option_expired_date += expired_date_list

    def init_index_option_remain_day(self):
        for date in self.option_expired_date:
            start_date = datetime.datetime.now().date()
            end_date = datetime.datetime.strptime(date, "%Y%m%d").date()
            day_count = count_trading_days(start_date, end_date, HOLIDAYS)
            self.index_option_remain_day.append(round((day_count - 1) / YEAR_TRADING_DAY, 4))


    def init_index_option_month_strike_num(self):
        """
        生成每个期权品种月份对应的行权价数量列表。
        假设期权格式为：'HO2410-C-4100'，表示品种HO，月份2410，行权价4100
        """

        for name in self.index_option_month_forward_id:
            self.index_option_month_strike_num.append(self.option_series_dict[name].get_num_strike_price())

        self.index_option_month_strike_max_num = max(self.index_option_month_strike_num)

    def init_index_option_market_data(self):
        """
        假设有 len(self.index_option_month_forward_id) 个月份，每个期权品种最多有 2 种看涨/看跌期权，index_option_month_strike_max_num 个行权价，每个行权价有 7 个字段
        :return: 
        """
        self.index_option_market_data = np.zeros((len(self.index_option_month_forward_id), 2, self.index_option_month_strike_max_num, 7))

        for i, name in enumerate(self.index_option_month_forward_id):
            strike_prices = self.option_series_dict[name].get_all_strike_price()
            for j, strike_price in enumerate(strike_prices):
                self.index_option_market_data[i, 0, j, 0] = strike_price
                self.index_option_market_data[i, 1, j, 0] = strike_price

    def init_index_option_month_forward_price(self):
        """
        # 0（远期有效性），1（远期ask），2（远期bid），3（Askstrike），4（BIDstrike），5（ATMS有效性），6（Ask），7（Bid），8（K1），9（K2），10（K3），11（K4），12（ISask），13（ISbid）
        """
        self.index_option_month_forward_price = np.zeros((len(self.index_option_month_forward_id), 14))

    def init_index_option_month_atm_vol(self):
        self.index_option_month_atm_vol = np.zeros((len(self.index_option_month_forward_id), 15))

    def init_index_option_month_model_para(self):
        self.index_option_month_model_para = np.zeros((len(self.index_option_month_forward_id), 5))

    def init_index_option_month_t_iv(self):
        self.index_option_month_t_iv = np.zeros((len(self.index_option_month_forward_id), self.index_option_month_strike_max_num, 9))
        for i in range(len(self.index_option_month_forward_id)):
            # 行权价
            self.index_option_month_t_iv[i, :, 0] = self.index_option_market_data[i, 0, :, 0].copy()

    def init_index_option_month_greeks(self):
        self.index_option_month_greeks = np.zeros((len(self.index_option_month_forward_id), self.index_option_month_strike_max_num, 14))
        for i in range(len(self.index_option_month_forward_id)):
            # 行权价
            self.index_option_month_greeks[i, :, 0] = self.index_option_market_data[i, 0, :, 0].copy()

    def get_option(self, instrument_id):
        symbol = instrument_id.split('-')[0]
        strike_price = instrument_id.split('-')[-1]
        if instrument_id[7] == "C":
            return self.option_series_dict[symbol][strike_price][0]
        elif instrument_id[7] == "P":
            return self.option_series_dict[symbol][strike_price][1]



    # def index_option_vol_calculator(self):
    #     while True:
    #         local_time_start = time.time()
    #         for i in range(len(self.index_option_month_forward_id)):
    #             # 计算forward价格，获取两侧行权价，标记FW价格无效，loc_index_month_available,标记IS无法取得,loc_index_IS_available
    #             # 将全局变量赋予局部变量：时间,P,C可交易性，行权价,P,C价格，R,D
    #
    #

    # def index_option_implyS(loc_Oprion_C_Price_available, loc_Oprion_P_Price_available, loc_Oprion_strike,
    #                         loc_Oprion_C_ASK1_Price_available, loc_Oprion_C_BID1_Price_available,
    #                         loc_Oprion_P_ASK1_Price_available, loc_Oprion_P_BID1_Price_available,
    #                         loc_Index_optiom_Remaintimenumb, Index_option_Rumb, Index_option_Dumb, ):


    def index_option_imply_forward(self, option_call_available: [], option_put_available: [], option_strike: [],
                                   option_call_ask1_price: [], option_call_bid1_price: [],
                                   option_put_ask1_price: [], option_put_bid1_price: []):
        """
        @para
        """
        # 0（远期有效性），1（远期ask），2（远期bid），3（Askstrike），4（BIDstrike），5（ATMS有效性），6（Ask），7（Bid），8（K1），9（K2），10（K3），11（K4），12（ISask），13（ISbid）
        index_option_month_forward_price = [0] * 14
        # 至少有一组C与P必须同时可交易才能生成forward，否则返回-1
        if 1 in option_call_available * option_put_available:
            index_option_month_forward_price[0] = 1
            # 生成可交易的组生成 01 序列
            middle_available = (option_call_available * option_put_available) != 0
            # midaskarray = loc_Oprion_C_ASK1_Price_available[midarray] - loc_Oprion_P_BID1_Price_available[midarray] + \
            #               loc_Oprion_strike[midarray] * math.exp(-loc_Index_optiom_Remaintimenumb * Index_option_Rumb)



