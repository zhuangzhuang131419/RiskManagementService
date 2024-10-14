import math
from symbol import return_stmt

import numpy as np
import pandas as pd
import py_vollib_vectorized

from helper.helper import INTEREST_RATE


# put call parity
def calculate_prices(call_prices, put_prices, strike_prices, remain_time):
    # 期权平价公式 C-P=S-Ke^(-rt) => S=C-P+Ke^(-rt)
    # C是欧式看涨期权的价格；
    # P是欧式看跌期权的价格；
    # S是标的资产的当前价格；
    # K是期权的执行价格（行权价）；
    # r是无风险利率（通常为年化利率）；
    # t是期权到期时间和当前时间之间的差异（以年为单位）；
    # e是自然对数的底数。
    """计算标的的价格"""
    return call_prices - put_prices + strike_prices * math.exp(-INTEREST_RATE * remain_time)

def calculate_x_distance(S, K, t, r, v, q):
    """
    计算标的资产当前价格与期权执行价之间的标准差距离。

    参数：
    S (float): 当前标的资产价格（如股票价格）。
    K (float): 期权的执行价（行权价）。
    t (float): 到期时间，表示距离期权到期的时间（以年为单位）。
    r (float): 无风险利率（如国债利率）。
    v (float): 标的资产的波动率，衡量价格波动的幅度。
    q (float): 股息收益率，表示期权到期前的股息支付率。

    """
    # 计算价格差异并考虑时间、利率和股息的影响
    x_distance = math.log(K / (S * math.exp(t * (r - q)))) / (v * math.sqrt(t))
    return x_distance


def calculate_imply_volatility(option_type: str, underlying_price: float, strike_price: float, remaining_year: float, interest_rate: float, option_price: float, dividend_rate: float) -> float:
    """
    计算期权的隐含波动率。

    参数说明：
    option_type: 期权类型，'c' 表示看涨期权，'p' 表示看跌期权。
    underlying_price: 当前标的资产价格（现价）。
    strike_price: 期权的行权价。
    remaining_year: 距到期时间（以年为单位）。
    interest_rate: 无风险利率（通常为年化利率）。
    price: 期权的市场价格（即市场上期权的实际成交价格）。
    dividend_rate: 分红收益率（股息或其他形式的收益率）。

    返回：
    float
        隐含波动率（若计算成功且大于 0），否则返回 None。
    """
    try:
        # 计算隐含波动率，忽略计算中的错误
        volatility = py_vollib_vectorized.vectorized_implied_volatility(price=option_price, S=underlying_price, K=strike_price, t=remaining_year, r=interest_rate, flag=option_type, q=dividend_rate, model='black_scholes_merton', return_as='numpy', on_error='ignore')

        # 只返回大于 0 的波动率
        if volatility > 0:
            return volatility
        else:
            return -1
    except Exception as e:
        # 捕获任何异常并返回 None
        print(f"Error calculating implied volatility: {e}")
        return -1

def calculate_delta(option_type: str, underlying_price: float, strike_price: float, remaining_year: float, interest_rate: float, volatility: float, dividend_rate: float):
    try:
        gamma = py_vollib_vectorized.vectorized_delta(flag=option_type, S=underlying_price, K=strike_price, t=remaining_year, r=interest_rate, sigma=volatility, q=dividend_rate, model='black_scholes_merton', return_as='numpy')
        return gamma
    except Exception as e:
        print(f"Error calculating delta: {e}")

def calculate_gamma(option_type: str, underlying_price: float, strike_price: float, remaining_year: float, interest_rate: float, volatility: float, dividend_rate: float):
    try:
        gamma = py_vollib_vectorized.vectorized_gamma(flag=option_type, S=underlying_price, K=strike_price, t=remaining_year, r=interest_rate, sigma=volatility, q=dividend_rate, model='black_scholes_merton', return_as='numpy')
        return gamma
    except Exception as e:
        print(f"Error calculating gamma: {e}")

def calculate_vega(option_type: str, underlying_price: float, strike_price: float, remaining_year: float, interest_rate: float, option_price: float, dividend_rate: float):
    try:
        vega = py_vollib_vectorized.vectorized_vega(option_type, underlying_price, strike_price, remaining_year, interest_rate, option_type, q=dividend_rate, model='black_scholes_merton', return_as='numpy')
        return vega
    except Exception as e:
        print(f"Error calculating vega: {e}")

def estimate_atm_volatility(strike_price_list, volatility_list, price):
    # volatility = a0 + a1 * strike_price + a2 * strike_price ^ 2
    inverse = np.linalg.inv(np.vstack((np.array([1, 1, 1]), strike_price_list, strike_price_list ** 2)).T)
    para = np.matmul(inverse, volatility_list)
    # 将当前价格 price 代入拟合的二次多项式
    return np.dot(np.array([1, price, price * price]), para)
