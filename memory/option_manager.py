import datetime
import math
import threading
import time

from typing import Dict, Tuple

from helper.calculator import *
from helper.wing_model import *
from helper.helper import INTEREST_RATE, DIVIDEND
from model.instrument.option import Option, OptionTuple
from model.instrument.option_series import OptionSeries
from model.memory.atm_volatility import ATMVolatility
from model.memory.greeks import Greeks
from model.memory.imply_price import ImplyPrice
from model.memory.t_imply_volatility import TImplyVolatility
from model.memory.wing_model_para import WingModelPara


class OptionManager:
    # 期权链
    option_series_dict: Dict[str, OptionSeries] = {}

    # 期权品种月份列表
    index_option_month_forward_id = []

    def __init__(self, index_options):
        self.init_option_series(index_options)
        self.init_index_option_month_id()

        self.greeks_lock = threading.Lock()

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
        for symbol, options_list in option_series_dict.items():
            self.option_series_dict[symbol] = OptionSeries(symbol, options_list)



    def init_index_option_month_id(self):
        """
        生成唯一的期权月份列表，格式如：["HO2410","HO2411","HO2412","HO2501","HO2503","HO2506",…,…]
        """

        for name in self.option_series_dict.keys():
            self.index_option_month_forward_id.append(name)

        self.index_option_month_forward_id = sorted(self.index_option_month_forward_id)


    # def get_option(self, instrument_id):
    #     symbol = instrument_id.split('-')[0]
    #     strike_price = instrument_id.split('-')[-1]
    #     if instrument_id[7] == "C":
    #         return self.option_series_dict[symbol].strike_price_options[strike_price].call
    #     elif instrument_id[7] == "P":
    #         return self.option_series_dict[symbol].strike_price_options[strike_price].put



    def index_volatility_calculator(self):
        while True:
            timestamp = time.time()
            for i, symbol in enumerate(self.index_option_month_forward_id):
                # 计算forward价格，获取两侧行权价，标记FW价格无效，loc_index_month_available,标记IS无法取得,loc_index_IS_available
                self.index_option_imply_forward_price(i, symbol)
                if self.option_series_dict[symbol].imply_price.future_valid == -1:
                    self.option_series_dict[symbol].atm_volatility = ATMVolatility()
                    # print(f'{symbol} month tick error')
                    continue
                else:
                    self.calculate_atm_para(i, symbol)
                    self.calculate_index_option_month_t_iv(i, symbol)
                    self.calculate_wing_model_para(i, symbol)

                    with self.greeks_lock:
                        self.calculate_greeks(i, symbol)

            time.sleep(2)

    def calculate_greeks(self, index, symbol):
        underlying_price = (self.option_series_dict[symbol].imply_price.imply_s_ask + self.option_series_dict[symbol].imply_price.imply_s_bid) / 2
        remain_time = self.option_series_dict[index].remaining_year
        volatility = self.option_series_dict[symbol].atm_volatility.atm_volatility_protected
        k1 = self.option_series_dict[symbol].wing_model_para.k1
        k2 = self.option_series_dict[symbol].wing_model_para.k2
        b = self.option_series_dict[symbol].wing_model_para.b

        # print(f"k1: {k1}, k2: {k2}, b: {b}")

        for strike_price, option_tuple in self.option_series_dict[symbol].strike_price_options.items():
            option_tuple.call.greeks.delta = v_delta('c', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]
            option_tuple.put.greeks.delta = v_delta('p', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]

            option_tuple.call.greeks.gamma = v_gamma_percent('c', underlying_price, strike_price, remain_time, INTEREST_RATE,  volatility, DIVIDEND, k1, k2, b)[0]
            option_tuple.put.greeks.gamma = v_gamma_percent('p', underlying_price, strike_price, remain_time, INTEREST_RATE,  volatility, DIVIDEND, k1, k2, b)[0]

            option_tuple.call.greeks.vega = v_vega('c', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]
            option_tuple.put.greeks.vega = v_vega('p', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]

            option_tuple.call.greeks.theta = v_theta('c', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]
            option_tuple.put.greeks.theta = v_theta('p', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]

            option_tuple.call.greeks.vanna_sv = v_vannasv('c', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]
            option_tuple.put.greeks.vanna_sv = v_vannasv('p', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]

            option_tuple.call.greeks.vanna_vs = v_vannavs('c', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]
            option_tuple.put.greeks.vanna_vs = v_vannavs('p', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]

            option_tuple.call.greeks.db = v_db('c', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]
            option_tuple.put.greeks.db = v_db('p', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]

            option_tuple.call.greeks.vomma = v_vomma('c', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]
            option_tuple.put.greeks.vomma = v_vomma('p', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]

            option_tuple.call.greeks.dk1 = v_dk1('c', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]
            option_tuple.put.greeks.dk1 = v_dk1('p', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]

            option_tuple.call.greeks.dk2 = v_dk2('c', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]
            option_tuple.put.greeks.dk2 = v_dk2('p', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]

            option_tuple.call.greeks.charm = v_charm('c', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]
            option_tuple.put.greeks.charm = v_charm('p', underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND, k1, k2, b)[0]


    def calculate_wing_model_para(self, index, symbol):
        # underlying_price = (self.index_option_month_forward_price[index, 12] + self.index_option_month_forward_price[index, 13]) / 2
        underlying_price = (self.option_series_dict[symbol].imply_price.imply_s_ask + self.option_series_dict[symbol].imply_price.imply_s_bid) / 2
        strike_prices = self.option_series_dict[symbol].get_all_strike_price()
        remain_time = self.option_series_dict[symbol].remaining_year
        volatility = self.option_series_dict[symbol].atm_volatility.atm_volatility_protected

        strike_price_num = self.option_series_dict[symbol].get_num_strike_price()

        wing_model_para = WingModelPara()

        available_num = 0
        for strike_price, option_tuple in self.option_series_dict[symbol].strike_price_options.items():
            if option_tuple.imply_volatility.sample_valid != 0:
                available_num += 1

        if available_num <= 3:
            wing_model_para.S = underlying_price
            wing_model_para.k1 = 0
            wing_model_para.k2 = 0
            wing_model_para.b = 0
            wing_model_para.residual = -1
            self.option_series_dict[symbol].wing_model_para = wing_model_para
            return

        # 剔除掉
        cut_point = 2
        x_array = np.zeros((strike_price_num, 3))
        y_array = np.zeros(strike_price_num)



        for j in range(strike_price_num):
            x_distance = calculate_x_distance(S=underlying_price, K=strike_prices[j], t=remain_time, r=INTEREST_RATE, v=volatility, q=DIVIDEND)
            sample_available = self.option_series_dict[symbol].strike_price_options[strike_prices[j]].imply_volatility.sample_valid
            sample_volatility = self.option_series_dict[symbol].strike_price_options[strike_prices[j]].imply_volatility.sample_volatility
            if -cut_point < x_distance <= 0:
                x_array[j, 0] = x_distance * x_distance * sample_available
                x_array[j, 2] = x_distance * sample_available
                y_array[j] = (sample_volatility - volatility) * sample_available
            elif 0 < x_distance <= cut_point:
                x_array[j, 1] = x_distance * x_distance * sample_available
                x_array[j, 2] = x_distance * sample_available
                y_array[j] = (sample_volatility - volatility) * sample_available

        # 参数估计
        para_array = np.dot(np.dot(np.linalg.inv(np.dot(np.transpose(x_array), x_array)), np.transpose(x_array)),y_array)
        # 残差序列
        residual = y_array - x_array @ para_array

        wing_model_para.S = underlying_price
        wing_model_para.k1 = para_array[0]
        wing_model_para.k2 = para_array[1]
        wing_model_para.b = para_array[2]
        wing_model_para.residual = (residual@residual) / available_num

        self.option_series_dict[symbol].wing_model_para = wing_model_para


    def calculate_atm_para(self, index, symbol):
        # K1 左二 K2 左一 K3 右一 k4 右二
        k1_strike = self.option_series_dict[symbol].imply_price.k1
        k2_strike = self.option_series_dict[symbol].imply_price.k2
        k3_strike = self.option_series_dict[symbol].imply_price.k3
        k4_strike = self.option_series_dict[symbol].imply_price.k4

        # option ask bid 取中间价
        remain_time = self.option_series_dict[symbol].remaining_year
        # 对应标的物的远期价格
        underlying_price = (self.option_series_dict[symbol].imply_price.imply_s_ask + self.option_series_dict[
            symbol].imply_price.imply_s_bid) / 2

        forward_underlying_price = underlying_price * math.exp(remain_time * (INTEREST_RATE - DIVIDEND))

        atm_volatility = ATMVolatility()

        # 判断离平值期权最近的
        if k2_strike != -1 and k3_strike != -1:

            strike_prices = [k1_strike, k2_strike, k3_strike, k4_strike]
            volatility_dict: Dict[float, tuple] = {}

            for k_strike_price in strike_prices:
                k_option_tuple = self.option_series_dict[symbol].strike_price_options[k_strike_price]
                call_price = (k_option_tuple.call.market_data.ask_prices[0] + k_option_tuple.call.market_data.bid_prices[0]) / 2
                put_price = (k_option_tuple.put.market_data.ask_prices[0] + k_option_tuple.put.market_data.bid_prices[0]) / 2
                call_volatility = calculate_imply_volatility('c', underlying_price, k_strike_price, remain_time, INTEREST_RATE, call_price, DIVIDEND)
                put_volatility = calculate_imply_volatility('p', underlying_price, k_strike_price, remain_time, INTEREST_RATE, put_price, DIVIDEND)
                volatility_dict[k_strike_price] = (call_volatility, put_volatility)

            # 左右行权价计算的波动率无效
            if volatility_dict[k2_strike][0] != -1 and volatility_dict[k2_strike][1] != -1 and volatility_dict[k3_strike][0] != -1 and volatility_dict[k3_strike][1] != -1:
                atm_volatility.atm_valid = 1
                # 对于K1 K4 行权价只计算call 或者 put
                atm_volatility.k1_volatility = volatility_dict[k1_strike][1] # put
                atm_volatility.k2_volatility = (volatility_dict[k2_strike][0] + volatility_dict[k2_strike][1]) / 2
                atm_volatility.k3_volatility = (volatility_dict[k3_strike][0] + volatility_dict[k3_strike][1]) / 2
                atm_volatility.k4_volatility = volatility_dict[k4_strike][0] # call

                volatility = [atm_volatility.k1_volatility, atm_volatility.k2_volatility, atm_volatility.k3_volatility, atm_volatility.k4_volatility]

                if atm_volatility.k1_volatility != -1 and atm_volatility.k4_volatility == -1:
                    # 左中有效 右无效
                    atm_volatility.atm_volatility_protected = estimate_atm_volatility(np.array([k1_strike, k2_strike, k3_strike]), np.array(volatility[0:3]), forward_underlying_price)
                if atm_volatility.k1_volatility == -1 and atm_volatility.k4_volatility != -1:
                    # 左无效 右中有效
                    atm_volatility.atm_volatility_protected = estimate_atm_volatility(np.array([k2_strike, k3_strike, k4_strike]), np.array(volatility[1:]), forward_underlying_price)
                if atm_volatility.k1_volatility != -1 and atm_volatility.k4_volatility != -1:
                    # 全部有效
                    atm_volatility.atm_volatility_protected = (estimate_atm_volatility(np.array([k1_strike, k2_strike, k3_strike]), np.array(volatility[0:3]),forward_underlying_price) +
                                                               estimate_atm_volatility(np.array([k2_strike, k3_strike, k4_strike]), np.array(volatility[1:]),forward_underlying_price)) / 2
                if atm_volatility.k1_volatility == -1 and atm_volatility.k4_volatility == -1:
                    # 仅中间有效
                    atm_volatility.atm_volatility_protected = self.option_series_dict[symbol].atm_volatility.atm_volatility_protected

        # 如果波动率自始至终都是0或者-1，则平值波动率参数全为-1
        if atm_volatility.atm_volatility_protected > 0:
            atm_volatility.atm_gamma = calculate_gamma('c', underlying_price, forward_underlying_price, remain_time, INTEREST_RATE, atm_volatility.atm_volatility_protected, DIVIDEND)
            atm_volatility.atm_vega = calculate_vega('c', underlying_price, forward_underlying_price, remain_time, INTEREST_RATE, atm_volatility.atm_volatility_protected, DIVIDEND)

            for i in range(7):
                atm_volatility.volatility_points[i] = math.exp((i * 0.66 - 1.98) * atm_volatility.atm_volatility_protected * math.sqrt(remain_time)) * forward_underlying_price


        self.option_series_dict[symbol].atm_volatility = atm_volatility

    def calculate_index_option_month_t_iv(self, index, symbol):
        # 对应标的物的远期价格
        underlying_price = (self.option_series_dict[symbol].imply_price.imply_s_ask + self.option_series_dict[symbol].imply_price.imply_s_bid) / 2
        remain_time = self.option_series_dict[symbol].remaining_year
        volatility = self.option_series_dict[symbol].atm_volatility.atm_volatility_protected

        for strike_price, option_tuple in self.option_series_dict[symbol].strike_price_options.items():
            option_tuple.imply_volatility.strike_price = strike_price
            option_tuple.imply_volatility.c_ask_vol = calculate_imply_volatility('c', underlying_price, [strike_price], remain_time, INTEREST_RATE, option_tuple.call.market_data.ask_price, DIVIDEND)
            option_tuple.imply_volatility.c_bid_vol = calculate_imply_volatility('c', underlying_price, [strike_price], remain_time, INTEREST_RATE, option_tuple.call.market_data.bid_price, DIVIDEND)
            option_tuple.imply_volatility.p_ask_vol = calculate_imply_volatility('p', underlying_price, [strike_price], remain_time, INTEREST_RATE, option_tuple.put.market_data.ask_price, DIVIDEND)
            option_tuple.imply_volatility.p_bid_vol = calculate_imply_volatility('p', underlying_price, [strike_price], remain_time, INTEREST_RATE, option_tuple.put.market_data.bid_price, DIVIDEND)


        if volatility > 0:
            for strike_price, option_tuple in self.option_series_dict[symbol].strike_price_options.items():
                sample_delta = calculate_delta('c', underlying_price, [strike_price], remain_time, INTEREST_RATE, volatility, DIVIDEND)

                # 样本有效性
                option_tuple.imply_volatility.x_distance = calculate_x_distance(underlying_price, strike_price, remain_time, INTEREST_RATE, volatility, DIVIDEND)
                # 偏离一个标准差的距离，call 没有参考价值
                if option_tuple.imply_volatility.x_distance < -1.32:
                    if option_tuple.put.market_data.available == 1 and option_tuple.imply_volatility.p_bid_vol > 0:
                        option_tuple.imply_volatility.sample_valid = 1
                    else:
                        option_tuple.imply_volatility.sample_valid = 0

                    if option_tuple.imply_volatility.sample_valid > 0:
                        option_tuple.imply_volatility.sample_volatility = (option_tuple.imply_volatility.p_ask_vol + option_tuple.imply_volatility.p_bid_vol) / 2

                # 偏离一个标准差的距离，put 没有参考价值
                elif option_tuple.imply_volatility.x_distance > 1.32:

                    if option_tuple.call.market_data.available == 1 and option_tuple.imply_volatility.c_bid_vol > 0:
                        option_tuple.imply_volatility.sample_valid = 1
                    else:
                        option_tuple.imply_volatility.sample_valid = 0

                    if option_tuple.imply_volatility.sample_valid > 0:
                        option_tuple.imply_volatility.sample_volatility = (option_tuple.imply_volatility.c_ask_vol + option_tuple.imply_volatility.c_bid_vol) / 2

                else:

                    if option_tuple.call.market_data.available == 1 and option_tuple.imply_volatility.c_bid_vol > 0 and option_tuple.put.market_data.available == 1 and option_tuple.imply_volatility.p_bid_vol > 0:
                        option_tuple.imply_volatility.sample_valid = 1
                    else:
                        option_tuple.imply_volatility.sample_valid = 0

                    if option_tuple.imply_volatility.sample_valid > 0:
                        option_tuple.imply_volatility.sample_volatility = ((option_tuple.imply_volatility.c_ask_vol + option_tuple.imply_volatility.c_bid_vol) * (1 - sample_delta) +
                                                                     (option_tuple.imply_volatility.c_ask_vol + option_tuple.imply_volatility.c_bid_vol) * sample_delta) / 2





    def index_option_imply_forward_price(self, index, symbol):
        """
        计算一个symbol期权下所有的远期价格
        [0]（远期有效性） [1] 远期 ask [2] 远期 bid [3] ask strike [4] bid strike [5]（ATMS有效性），[6] atm ask [7] atm bid [8]（K1 平值左侧第二行权价），9（K2 平值左侧行权价），10（K3 平值右侧行权价），11（K4 平值右侧第二行权价），12（ISask），13（ISbid）
        @para
        """
        strike_prices: [] = sorted(list(self.option_series_dict[symbol].strike_price_options.keys()))
        remain_time = self.option_series_dict[symbol].remaining_year

        imply_price = ImplyPrice()

        forward_ask_prices: Dict[float, float] = {}
        forward_bid_prices: Dict[float, float] = {}
        # print(f"options:{self.option_series_dict[symbol].strike_price_options.items()}")
        for strike_price, option_tuple in self.option_series_dict[symbol].strike_price_options.items():

            call_option = option_tuple.call
            put_option = option_tuple.put
            # print(f"strike price: {strike_price} call:{call_option}, put:{put_option}")
            # 至少有一组C与P必须同时可交易才能生成forward，否则返回 - 1
            if call_option.market_data.available and put_option.market_data.available:
                forward_ask_prices[strike_price] = calculate_prices(call_option.market_data.ask_prices[0], put_option.market_data.bid_prices[0], strike_price, remain_time)
                forward_bid_prices[strike_price] = calculate_prices(call_option.market_data.bid_prices[0], put_option.market_data.ask_prices[0], strike_price, remain_time)

        if len(forward_ask_prices) == 0:
            imply_price.future_valid = -1
        else:
            imply_price.future_valid = 1
            imply_price.ask_strike, imply_price.forward_ask = min(forward_ask_prices.items(), key=lambda x: x[1])
            imply_price.bid_strike, imply_price.forward_bid = max(forward_ask_prices.items(), key=lambda x: x[1])
            forward_price = (imply_price.forward_ask + imply_price.forward_bid) / 2 * math.exp(remain_time * (INTEREST_RATE - DIVIDEND))

            # 查找ATM（平值期权）位置
            atm_location = [-1, -1]
            for j, strike in enumerate(strike_prices):
                if forward_price < strike:
                    atm_location = [j - 1, j]
                    break

            # 如果没有找到有效的ATM位置
            if -1 in atm_location:
                imply_price.imply_s_ask = imply_price.forward_ask
                imply_price.imply_s_bid = imply_price.forward_bid
            else:
                # 检查两侧ATM期权的有效性

                k2_strike_price = strike_prices[atm_location[0]]
                k2_option: OptionTuple = self.option_series_dict[symbol].strike_price_options[k2_strike_price]
                k2_tradable = k2_option.call.market_data.available and k2_option.put.market_data.available

                k3_strike_price = strike_prices[atm_location[1]]
                k3_option: OptionTuple = self.option_series_dict[symbol].strike_price_options[k3_strike_price]
                k3_tradable = k3_option.call.market_data.available and k3_option.put.market_data.available

                if k2_tradable and k3_tradable:
                    imply_price.atm_valid = 1

                    # 左侧和右侧的ask和bid价格
                    # left_ask = calculate_prices(call_ask1_price[atm_location[0]], put_bid1_price[atm_location[0]], strike_prices[atm_location[0]], remain_time)
                    left_ask = calculate_prices(k2_option.call.market_data.ask_prices[0], k2_option.put.market_data.bid_prices[0], imply_price.k2, remain_time)
                    # left_bid = calculate_prices(call_bid1_price[atm_location[0]], put_ask1_price[atm_location[0]], strike_prices[atm_location[0]], remain_time)
                    left_bid = calculate_prices(k2_option.call.market_data.bid_prices[0], k2_option.put.market_data.ask_prices[0], imply_price.k2, remain_time)

                    # right_ask = calculate_prices(call_ask1_price[atm_location[1]], put_bid1_price[atm_location[1]], strike_prices[atm_location[1]], remain_time)
                    right_ask = calculate_prices(k3_option.call.market_data.ask_prices[0], k3_option.put.market_data.bid_prices[0], imply_price.k3, remain_time)
                    # right_bid = calculate_prices(call_bid1_price[atm_location[1]], put_ask1_price[atm_location[1]], strike_prices[atm_location[1]], remain_time)
                    right_bid = calculate_prices(k3_option.call.market_data.bid_prices[0], k3_option.put.market_data.ask_prices[0], imply_price.k3, remain_time)

                    # 插值计算ask和bid价格
                    # strike_diff = strike_prices[atm_location[1]] - strike_prices[atm_location[0]]
                    strike_diff = imply_price.k3 - imply_price.k2
                    forward_diff = forward_price - imply_price.k2

                    imply_price.atms_ask = (imply_price.k3 - forward_price) / strike_diff * left_ask + forward_diff / strike_diff * right_ask
                    imply_price.atms_bid = (imply_price.k3 - forward_price) / strike_diff * left_bid + forward_diff / strike_diff * right_bid

                    imply_price.imply_s_ask = imply_price.atms_ask
                    imply_price.imply_s_bid = imply_price.atms_bid

                    if atm_location[0] > 0:
                        k1_strike_price = strike_prices[atm_location[0] - 1]
                        k1_option: OptionTuple = self.option_series_dict[symbol].strike_price_options[k1_strike_price]
                        k1_tradable = k1_option.call.market_data.available and k1_option.put.market_data.available
                        if k1_tradable:
                            imply_price.k1 = k1_strike_price

                    # 检查两侧的额外执行价是否有效
                    if atm_location[1] < len(strike_prices) - 1:
                        k4_strike_price = strike_prices[atm_location[0] - 1]
                        k4_option: OptionTuple = self.option_series_dict[symbol].strike_price_options[k4_strike_price]
                        k4_tradable = k4_option.call.market_data.available and k4_option.put.market_data.available
                        if k4_tradable:
                            imply_price.k4 = k4_strike_price

                    imply_price.k2 = k2_strike_price
                    imply_price.k3 = k3_strike_price

                else:
                    # 如果atm算不出来 那就只能拿远期的bid ask
                    imply_price.imply_s_ask = imply_price.forward_ask
                    imply_price.imply_s_bid = imply_price.forward_bid

        self.option_series_dict[symbol].imply_price = imply_price