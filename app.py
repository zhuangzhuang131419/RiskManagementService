import time
import numpy as np
from typing import Dict

from helper.helper import filter_index_option, filter_etf
from memory.option_manager import OptionManager
from model.ctp_manager import CTPManager
from model.exchange.exchange import Exchange
from model.exchange.exchange_type import ExchangeType
from model.instrument.option_series import OptionSeries
from model.memory.atm_volatility import ATMVolatility
from model.memory.wing_model_para import WingModelPara
from model.response.option_market_resp import OptionMarketResp, OptionData
from model.response.option_greeks import OptionGreeksData, OptionGreeksResp
from model.response.option_resp_base import StrikePrices
from model.response.user import UserResp
from model.response.wing_model_resp import WingModelResp

np.set_printoptions(suppress=True)
from threading import Thread

from flask import Flask, jsonify, render_template, send_from_directory, request

app = Flask(__name__, static_folder='./frontend/build')

# 路由所有到 React 的前端应用
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and path.startswith('static'):
        # 如果请求的是静态文件，返回对应的静态文件
        return send_from_directory(app.static_folder, path)
    else:
        # 否则返回 React 构建后的 index.html
        return send_from_directory(app.static_folder, 'index.html')

ctp_manager = CTPManager()

def init_ctp():
    # 初始化
    global ctp_manager
    ctp_manager.switch_to_user("test123")


def main():
    future_manager = ctp_manager.current_user.memory.future_manager
    se_option_manager = ctp_manager.current_user.memory.se_option_manager
    cffex_option_manager = ctp_manager.current_user.memory.cffex_option_manager

    if se_option_manager is not None:
        print('当前订阅期权合约数量为：{}'.format(len(ctp_manager.current_user.memory.se_option_manager.option_series_dict)))
        print('当前订阅期权合约到期月为：{}'.format(ctp_manager.current_user.memory.se_option_manager.option_series_dict.keys()))

    if future_manager is not None:
        print('当前订阅期货合约数量为：{}'.format(len(ctp_manager.current_user.memory.future_manager.index_futures_dict)))
        print('当前订阅期货合约月份为：{}'.format(ctp_manager.current_user.memory.future_manager.index_future_month_id))

    if cffex_option_manager is not None:
        print('当前订阅期权合约数量为：{}'.format(len(ctp_manager.current_user.memory.cffex_option_manager.option_series_dict)))
        print('当前订阅期权合约月份为：{}'.format(ctp_manager.current_user.memory.cffex_option_manager.index_option_month_forward_id))
        print('当前订阅期权合约行权价为：{}'.format(ctp_manager.current_user.memory.cffex_option_manager.option_series_dict['HO20241115'].strike_price_options.keys()))

    # ctp_manager.current_user.query_investor_position(ExchangeType.SSE.name)
    # ctp_manager.current_user.query_investor_position(ExchangeType.SZSE.name)
    # ctp_manager.current_user.query_investor_position_detail(ExchangeType.SSE.name)
    # ctp_manager.current_user.query_investor_position_detail(ExchangeType.SZSE.name)




    # print('HO2410的看涨期权的第一个行权价的行权价：{}'.format(ctp_manager.memory.option_manager.index_option_market_data[0, 0, 0, 0]))
    # print('HO2410的看涨期权的第二个行权价的行权价：{}'.format(
    #     ctp_manager.memory.option_manager.index_option_market_data[0, 0, 1, 0]))
    Thread(target=ctp_manager.tick).start()
    if cffex_option_manager is not None:
        Thread(target=ctp_manager.current_user.memory.cffex_option_manager.index_volatility_calculator).start()
    if se_option_manager is not None:
        Thread(target=ctp_manager.current_user.memory.se_option_manager.index_volatility_calculator).start()


    # print('HO2410的看涨期权的第一个行权价相关信息：{}'.format(
    #     ctp_manager.memory.option_manager.index_option_market_data[0, 0, 0]))
    # print('HO2410一共有几个行权价: {}'.format(memory_manager.option_manager.option_month_strike_prices['HO2410']))
    # print('当前订阅期权合约行权价数量为：{}'.format(memory_manager.option_manager.option_month_strike_num))



    # 模拟下单
    # ctp_manager.insert_order('IF2412', Direction.BUY_OPEN, 4000, 2)

    # ctp_manager.query_investor_position_detail()

    while True:
        # if cffex_option_manager is not None:
            # print(f"{cffex_option_manager.option_series_dict['HO20241115'].imply_price}")
            # print(f"{cffex_option_manager.option_series_dict['HO20241115'].strike_price_options[2425].call.market_data}")
            # print(f"{cffex_option_manager.option_series_dict['HO20241115'].strike_price_options[2425].put.market_data}")
            # k1_volatility = ctp_manager.memory.option_manager.index_option_month_atm_volatility[0, 1]
            # k2_volatility = ctp_manager.memory.option_manager.index_option_month_atm_volatility[0, 2]
            # k3_volatility = ctp_manager.memory.option_manager.index_option_month_atm_volatility[0, 3]
            # k4_volatility = ctp_manager.memory.option_manager.index_option_month_atm_volatility[0, 4]
            # atm_volatility = ctp_manager.memory.option_manager.index_option_month_atm_volatility[0, 5]
            # # atm_vega = ctp_manager.memory.option_manager.index_option_month_atm_volatility[0, 6]
            # print(f'HO2410的atm相关信息：k1_volatility: {k1_volatility}, k2_volatility: {k2_volatility}, k3_volatility: {k3_volatility}, k4_volatility: {k4_volatility}, atm_volatility: {atm_volatility}, atm_vega: {atm_vega}')



        # strike_index = 22
        # strike_price = ctp_manager.memory.option_manager.index_option_market_data[1, 0, strike_index, 0]
        # timestamp = ctp_manager.memory.option_manager.index_option_market_data[1, 0, strike_index, 1]
        # bid_price = ctp_manager.memory.option_manager.index_option_market_data[1, 0, strike_index, 2]
        # bid_volume = ctp_manager.memory.option_manager.index_option_market_data[1, 0, strike_index, 3]
        # ask_price = ctp_manager.memory.option_manager.index_option_market_data[1, 0, strike_index, 4]
        # ask_volume = ctp_manager.memory.option_manager.index_option_market_data[1, 0, strike_index, 5]
        # print(f'HO2411的看涨期权的第23个行权价相关信息：行权价{strike_price}, 时间{timestamp}, 买一价{bid_price}, 买一量{bid_volume}, 卖一价{ask_price}, 卖一量{ask_volume}')
        # strike_price = ctp_manager.memory.option_manager.index_option_market_data[1, 1, strike_index, 0]
        # timestamp = ctp_manager.memory.option_manager.index_option_market_data[1, 1, strike_index, 1]
        # bid_price = ctp_manager.memory.option_manager.index_option_market_data[1, 1, strike_index, 2]
        # bid_volume = ctp_manager.memory.option_manager.index_option_market_data[1, 1, strike_index, 3]
        # ask_price = ctp_manager.memory.option_manager.index_option_market_data[1, 1, strike_index, 4]
        # ask_volume = ctp_manager.memory.option_manager.index_option_market_data[1, 1, strike_index, 5]
        # print(f'HO2411的看跌期权的第23个行权价相关信息：行权价{strike_price}, 时间{timestamp}, 买一价{bid_price}, 买一量{bid_volume}, 卖一价{ask_price}, 卖一量{ask_volume}')
        # i = 0
        # call_delta = ctp_manager.memory.option_manager.index_option_month_greeks[1, i, 1]
        # put_delta = ctp_manager.memory.option_manager.index_option_month_greeks[1, i, 2]
        # gamma = ctp_manager.memory.option_manager.index_option_month_greeks[1, i, 3]
        # vega = ctp_manager.memory.option_manager.index_option_month_greeks[1, i, 4]
        # call_theta = ctp_manager.memory.option_manager.index_option_month_greeks[1, i, 5]
        # put_theta = ctp_manager.memory.option_manager.index_option_month_greeks[1, i, 6]
        # vanna_vs = ctp_manager.memory.option_manager.index_option_month_greeks[1, i, 7]
        # vanna_sv = ctp_manager.memory.option_manager.index_option_month_greeks[1, i, 8]
        # print(f'HO2411的看涨期权的第一个行权价Greeks相关信息：delta{call_delta}, gamma{gamma}, vega{vega}, theta{call_theta}')
        # print(
        #     f'HO2411的看跌期权的第一个行权价Greeks相关信息：delta{put_delta}, gamma{gamma}, vega{vega}, theta{put_theta}')
        # print('HO2410 期货价格:{}'.format(ctp_manager.memory.option_manager.index_option_month_forward_price[0, :]))
        time.sleep(10)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/users')
def get_users():
    result = []
    for user in ctp_manager.users.values():
        resp = UserResp(user.user_id, user.user_name)
        result.append(resp.to_dict())
    return jsonify(result)

@app.route('/api/get_all_market_data', methods=['GET'])
def get_all_market_data():
    # 返回当前行情数据
    return None

@app.route('/api/cffex/options', methods=['GET'])
def get_cffex_option():
    if ctp_manager.current_user.memory.cffex_option_manager is not None:
        return jsonify(ctp_manager.current_user.memory.cffex_option_manager.index_option_month_forward_id)
    else:
        return jsonify([])

@app.route('/api/se/options', methods=['GET'])
def get_se_option():
    if ctp_manager.current_user.memory.se_option_manager is not None:
        return jsonify(ctp_manager.current_user.memory.se_option_manager.index_option_month_forward_id)
    else:
        return jsonify([])

@app.route('/api/futures', methods=['GET'])
def get_all_future():
    if ctp_manager.current_user.memory.cffex_option_manager is not None:
        return jsonify(ctp_manager.current_user.memory.future_manager.index_future_month_id)
    else:
        return jsonify([])

@app.route('/api/se/option/greeks', methods=['GET'])
def get_se_option_greeks():
    symbol = request.args.get('symbol')
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404

    return get_option_greeks(symbol, ctp_manager.current_user.memory.se_option_manager)


@app.route('/api/cffex/option/greeks', methods=['GET'])
def get_cffex_option_greeks():
    symbol = request.args.get('symbol')
    print(symbol)
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404

    return get_option_greeks(symbol, ctp_manager.current_user.memory.cffex_option_manager)


def get_option_greeks(symbol: str, option_manager: OptionManager):
    resp = OptionGreeksResp(symbol)
    with option_manager.greeks_lock:
        for strike_price, option_tuple in option_manager.option_series_dict[symbol].strike_price_options.items():
            call_delta = option_tuple.call.greeks.delta
            put_delta = option_tuple.put.greeks.delta
            gamma = option_tuple.call.greeks.gamma
            vega = option_tuple.call.greeks.vega
            call_theta = option_tuple.call.greeks.theta
            put_theta = option_tuple.put.greeks.theta
            vanna_vs = option_tuple.call.greeks.vanna_vs
            vanna_sv = option_tuple.call.greeks.vanna_sv
            call_option = OptionGreeksData(call_delta, gamma, vega, call_theta, vanna_vs=vanna_vs, vanna_sv=vanna_sv)
            put_option = OptionGreeksData(put_delta, gamma, vega, put_theta, vanna_vs=vanna_vs, vanna_sv=vanna_sv)
            resp.strike_prices[strike_price] = StrikePrices(call_option, put_option)

    print(resp.to_dict())
    return jsonify(resp.to_dict())

@app.route('/api/se/option/wing_model', methods=['GET'])
def get_se_wing_model_by_symbol():
    symbol: str = request.args.get('symbol')
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404

    return get_wing_model_by_symbol(symbol, ctp_manager.current_user.memory.se_option_manager)

@app.route('/api/cffex/option/wing_model', methods=['GET'])
def get_cffex_wing_model_by_symbol():
    symbol: str = request.args.get('symbol')
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404

    return get_wing_model_by_symbol(symbol, ctp_manager.current_user.memory.cffex_option_manager)


def get_wing_model_by_symbol(symbol, option_manager: OptionManager):
    try:
        option_series: OptionSeries = option_manager.option_series_dict[symbol]
        wing_model_para: WingModelPara = option_series.wing_model_para
        atm_volatility: ATMVolatility = option_series.atm_volatility
        resp: WingModelResp = WingModelResp(atm_volatility.atm_volatility_protected, wing_model_para.k1, wing_model_para.k2, wing_model_para.b, atm_volatility.atm_valid)
        return jsonify(resp.to_dict())
    except ValueError:
        return jsonify({"error": f"Symbol {symbol} not found"}), 404

@app.route('/api/option/wing_model', methods=['GET'])
def get_all_customized_wing_model_para():
    resp: Dict[str, WingModelPara] = {}
    if ctp_manager.current_user.memory.se_option_manager is not None:
        resp = get_all_customized_wing_model_by_account(ctp_manager.current_user.memory.se_option_manager)

    if ctp_manager.current_user.memory.cffex_option_manager is not None:
        resp = {**get_all_customized_wing_model_by_account(ctp_manager.current_user.memory.cffex_option_manager), **resp}

    print(resp)
    return jsonify(resp)

def get_all_customized_wing_model_by_account(option_manager: OptionManager):
    resp: Dict[str, WingModelPara] = {}
    for symbol, option_series in option_manager.option_series_dict.items():
        wing_model_para: WingModelPara = option_series.customized_wing_model_para
        resp[symbol] = wing_model_para
    return resp

@app.route('/api/option/wing_model', methods=['POST'])
def set_customized_wing_model():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid or missing JSON data"}), 400
    for symbol, wing_para in data.items():
        para :WingModelPara = wing_para.get_json()
        option_manager = None
        if filter_index_option(symbol):
            option_manager = ctp_manager.current_user.memory.cffex_option_manager
        elif filter_etf(symbol):
            option_manager = ctp_manager.current_user.memory.se_option_manager

        if option_manager is not None:
            option_manager.option_series_dict[symbol].customized_wing_model_para.v = para.v
            option_manager.option_series_dict[symbol].customized_wing_model_para.k1 = para.k1
            option_manager.option_series_dict[symbol].customized_wing_model_para.k2 = para.k2
            option_manager.option_series_dict[symbol].customized_wing_model_para.b = para.b
    return jsonify({"message": "Customized wing model received"}), 200






if __name__ == "__main__":
    init_ctp()
    Thread(target=main).start()
    app.run(debug=True, use_reloader=False)


