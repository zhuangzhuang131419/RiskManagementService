import numpy as np
import py_vollib_vectorized

from utils.calculator import calculate_x_distance


class WingModel:
    def __init__(self, S, K, t, r, v, q, k1, k2, b):
        # 定义关键点
        xp0, xpc, xcc, xc0 = -4, -2, 2, 4

        # 计算分段函数的参数
        part1p = (2 * k1 * xpc + b) / (2 * (xpc - xp0))
        part2p = -(2 * k1 * xpc + b) / (xpc - xp0)
        part1c = (2 * k2 * xcc + b) / (2 * (xcc - xc0))
        part2c = -(2 * k2 * xcc + b) / (xcc - xc0)

        # 计算边界点的波动率
        sigma_p = k1 * xpc**2 + b * xpc + v - (part1p * xpc**2 + part2p * xp0 * xpc)
        sigma_c = k2 * xcc**2 + b * xcc + v - (part1c * xcc**2 + part2c * xc0 * xcc)

        # 计算波动率函数
        xx = calculate_x_distance(S, K, t, r, v, q)
        if xx < xp0:
            self.volatility = part1p * xp0 ** 2 + part2p * xp0 ** 2 + sigma_p
        elif xx < xpc:
            self.volatility = part1p * xx ** 2 + part2p * xp0 * xx + sigma_p
        elif xx < 0:
            self.volatility = k1 * xx ** 2 + b * xx + v
        elif xx < xcc:
            self.volatility = k2 * xx ** 2 + b * xx + v
        elif xx < xc0:
            self.volatility = part1c * xx ** 2 + part2c * xc0 * xx + sigma_c
        else:
            self.volatility = part1c * xc0 ** 2 + part2c * xc0 ** 2 + sigma_c

def v_delta(flag, S, K, t, r, v, q, k1, k2, b):
    if t < 1 / 254:
        t = 1 / 254
    model0 = WingModel(S, K, t, r, v, q, k1, k2, b)
    model1 = WingModel(S + 1, K, t, r, v, q, k1, k2, b)
    delta = (py_vollib_vectorized.vectorized_black_scholes_merton(flag, S + 1, K, t, r, model1.volatility, q=0, return_as='numpy')
             - py_vollib_vectorized.vectorized_black_scholes_merton(flag, S, K, t, r, model0.volatility, q=0, return_as='numpy'))
    return delta

def v_gamma_percent(flag, S, K, t, r, v, q, k1, k2, b):
    gamma =v_delta(flag, S*1.005, K, t, r, v, q, k1, k2, b)- v_delta(flag, S*0.995, K, t, r, v, q, k1, k2, b)
    return gamma

def v_charm(flag, S, K, t, r, v, q, k1, k2, b):
    charm =v_delta(flag, S, K, t, r, v, q, k1, k2, b)- v_delta(flag, S, K, t-1/254, r, v, q, k1, k2, b)
    return charm

def v_vega(flag, S, K, t, r, v, q, k1, k2, b):#vega
    if t<1/254:
        t=1/254
    model0 = WingModel(S, K, t, r, v-0.005, q, k1, k2, b)
    model1 = WingModel(S, K, t, r, v+0.005, q, k1, k2, b)
    vega = (py_vollib_vectorized.vectorized_black_scholes_merton(flag, S, K, t, r, model1.volatility, q=0, return_as='numpy')
            - py_vollib_vectorized.vectorized_black_scholes_merton(flag, S, K, t, r, model0.volatility, q=0, return_as='numpy'))
    return vega

def v_theta(flag, S, K, t, r, v, q, k1, k2, b):
    if t<1/254:
        t=1/254
    #保证wing中的t大于0
    model0= WingModel(S, K, t-1/255, r, v, q, k1, k2, b)
    model1 = WingModel(S, K, t, r, v, q, k1, k2, b)
    theta = (py_vollib_vectorized.vectorized_black_scholes_merton(flag, S, K, t - 1 / 255, r, model1.volatility, q=0, return_as='numpy')
             - py_vollib_vectorized.vectorized_black_scholes_merton(flag, S, K, t, r, model0.volatility, q=0, return_as='numpy'))
    return theta

def v_db(flag, S, K, t, r, v, q, k1, k2, b):
    if t<1/254:
        t=1/254
    model0 = WingModel(S, K, t, r, v, q, k1, k2, b)
    model1 = WingModel(S, K, t, r, v, q, k1, k2, b+0.01)
    db = (py_vollib_vectorized.vectorized_black_scholes_merton(flag, S, K, t, r, model1.volatility, q=0, return_as='numpy')
          - py_vollib_vectorized.vectorized_black_scholes_merton(flag, S, K, t, r, model0.volatility, q=0, return_as='numpy'))
    return db

def v_dk1(flag, S, K, t, r, v, q, k1, k2, b):
    if t<1/254:
        t=1/254
    model0 = WingModel(S, K, t, r, v, q, k1, k2, b)
    model1 = WingModel(S, K, t, r, v, q, k1+0.01, k2, b)
    dk1 = (py_vollib_vectorized.vectorized_black_scholes_merton(flag, S, K, t, r, model1.volatility, q=0, return_as='numpy')
           - py_vollib_vectorized.vectorized_black_scholes_merton(flag, S, K, t, r, model0.volatility, q=0, return_as='numpy'))
    return dk1

def v_dk2(flag, S, K, t, r, v, q, k1, k2, b):
    if t<1/254:
        t=1/254
    model0 = WingModel(S, K, t, r, v, q, k1, k2, b)
    model1 = WingModel(S, K, t, r, v, q, k1, k2+0.01, b)
    dk2 = (py_vollib_vectorized.vectorized_black_scholes_merton(flag, S, K, t, r, model1.volatility, q=0, return_as='numpy')
           - py_vollib_vectorized.vectorized_black_scholes_merton(flag, S, K, t, r, model0.volatility, q=0, return_as='numpy'))
    return dk2

def v_vannasv(flag, S, K, t, r, v, q, k1, k2, b):
    return v_delta(flag, S, K, t, r, v+0.005, q, k1, k2, b)- v_delta(flag, S, K, t, r, v-0.005, q, k1, k2, b)

def v_vannavs(flag, S, K, t, r, v, q, k1, k2, b):
    return v_vega(flag, S*1.005, K, t, r, v, q, k1, k2, b)-v_vega(flag, S*0.995, K, t, r, v, q, k1, k2, b)

def v_vomma(flag, S, K, t, r, v, q, k1, k2, b):
    return v_vega(flag, S, K, t, r, v+0.005, q, k1, k2, b) - v_vega(flag, S, K, t, r, v-0.005, q, k1, k2, b)