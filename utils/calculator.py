import math
from symbol import return_stmt

import numpy as np
import pandas as pd
import py_vollib_vectorized

from utils.helper import INTEREST_RATE


# put call parity
def calculate_prices(call_prices, put_prices, strike_prices, remain_time):
    """
    计算标的的价格
    期权平价公式 C-P=S-Ke^(-rt) => S=C-P+Ke^(-rt)
    C是欧式看涨期权的价格；
    P是欧式看跌期权的价格；
    S是标的资产的当前价格；
    K是期权的执行价格（行权价）；
    r是无风险利率（通常为年化利率）；
    t是期权到期时间和当前时间之间的差异（以年为单位）；
    e是自然对数的底数。

    返回：
        标的资产现货价格
    """
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
    if is_close(x_distance, 0.0, 8):
        print(f"S = {S}, K={K}, t={t}, r={r}, v={v}, q={q}")
    return x_distance


def calculate_imply_volatility(option_type, underlying_price, strike_price, remaining_year: float, interest_rate: float, option_price, dividend_rate):
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
        volatility = py_vollib_vectorized.vectorized_implied_volatility(price=option_price, S=underlying_price, K=strike_price, t=remaining_year, r=interest_rate, flag=option_type, q=dividend_rate, model='black_scholes_merton', return_as='array', on_error='ignore')[0]

        # 只返回大于 0 的波动率
        if volatility > 0:
            return volatility
        else:
            return -1
    except Exception as e:
        # 捕获任何异常并返回 None
        print(f"Error calculating implied volatility: {e}\n price = {option_price}\n S = {underlying_price}\n K = {strike_price}\n t = {remaining_year}\n r = {interest_rate}\n flag = {option_type}")
        return -1

def calculate_delta(option_type: str, underlying_price: float, strike_price, remaining_year: float, interest_rate: float, volatility: float, dividend_rate: float):
    try:
        delta = py_vollib_vectorized.vectorized_delta(flag=option_type, S=underlying_price, K=strike_price, t=remaining_year, r=interest_rate, sigma=volatility, q=dividend_rate, model='black_scholes_merton', return_as='array')[0]
        return delta
    except Exception as e:
        print(f"Error calculating delta: {e}\n S = {underlying_price}\n K = {strike_price}\n t = {remaining_year}\n r = {interest_rate}\n flag = {option_type}")

def calculate_gamma(option_type: str, underlying_price: float, strike_price: float, remaining_year: float, interest_rate: float, volatility: float, dividend_rate: float):
    try:
        gamma = py_vollib_vectorized.vectorized_gamma(flag=option_type, S=underlying_price, K=strike_price, t=remaining_year, r=interest_rate, sigma=volatility, q=dividend_rate, model='black_scholes_merton', return_as='array')[0]
        return gamma
    except Exception as e:
        print(f"Error calculating gamma: {e}")

def calculate_vega(option_type: str, underlying_price: float, strike_price: float, remaining_year: float, interest_rate: float, volatility: float, dividend_rate: float):
    try:
        vega = py_vollib_vectorized.vectorized_vega(flag=option_type, S=underlying_price, K=strike_price, t=remaining_year, r=interest_rate, sigma=volatility, q=dividend_rate, model='black_scholes_merton', return_as='array')[0]
        return vega
    except Exception as e:
        print(f"Error calculating vega: {e}")

#当K<0,or,t<0时返回nan，nan与任何数对比都会返回false，k=时严重错误，k取值使得option价格小于实值额度时，返回0，所以用>0做赛选可以避免除0/0以外的所有错误
def estimate_atm_volatility(strike_price_list: np.ndarray, volatility_list: np.ndarray, price: float):
    # 归一化数据
    mean_strike = np.mean(strike_price_list)
    normalized_strike = strike_price_list - mean_strike
    normalized_price = price - mean_strike

    # 构造设计矩阵
    A = np.vstack([np.ones_like(normalized_strike), normalized_strike, normalized_strike ** 2]).T
    para, _, _, _ = np.linalg.lstsq(A, volatility_list, rcond=None)

    # 使用归一化后的系数计算平值隐含波动率
    return para[0] + para[1] * normalized_price + para[2] * normalized_price ** 2

def is_close(a, b, precision=3):
    return round(a, precision) == round(b, precision)


if __name__ == '__main__':
    print(calculate_x_distance(3953.8691403968364, 4000, 0.464, 0.025, 0.2381077893692678, 0))
