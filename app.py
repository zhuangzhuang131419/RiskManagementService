import time
import numpy as np
from typing import Dict

from select import select

from helper.helper import filter_index_option, filter_etf_option
from memory.option_manager import OptionManager
from model.ctp_manager import CTPManager
from model.direction import Direction
from model.enum.baseline_type import BaselineType
from model.enum.exchange_type import ExchangeType
from model.instrument.option import Option
from model.instrument.option_series import OptionSeries
from model.memory.atm_volatility import ATMVolatility
from model.memory.wing_model_para import WingModelPara
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
    ctp_manager.switch_to_user("TestUser")

    print(f"{ctp_manager.current_user.memory.option_manager.instrument_transform_full_symbol}")

    # ctp_manager.current_user.query_investor_position_detail(ExchangeType.CFFEX.name)
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX.name, "HO2412-C-2400", Direction.BUY_OPEN, 288, 1)
    ctp_manager.current_user.query_investor_position(ExchangeType.CFFEX.name)

    future_manager = ctp_manager.current_user.memory.future_manager
    option_manager = ctp_manager.current_user.memory.option_manager

    if future_manager is not None:
        print('当前订阅期货合约数量为：{}'.format(len(ctp_manager.current_user.memory.future_manager.index_futures_dict)))
        print('当前订阅期货合约月份为：{}'.format(ctp_manager.current_user.memory.future_manager.index_future_symbol))

    if option_manager is not None:
        print('当前订阅期权合约数量为：{}'.format(
            len(ctp_manager.current_user.memory.option_manager.option_series_dict)))
        print('当前订阅期权合约月份为：{}'.format(ctp_manager.current_user.memory.option_manager.index_option_symbol))
        print('当前订阅期权合约行权价为：{}'.format(
            ctp_manager.current_user.memory.option_manager.option_series_dict[
                'HO20241115'].strike_price_options.keys()))

    Thread(target=ctp_manager.tick).start()
    if option_manager is not None:
        Thread(target=ctp_manager.current_user.memory.option_manager.index_volatility_calculator).start()

def main():


    # ctp_manager.current_user.query_investor_position(ExchangeType.SSE.name)
    # ctp_manager.current_user.query_investor_position(ExchangeType.SZSE.name)
    # ctp_manager.current_user.query_investor_position_detail(ExchangeType.SSE.name)
    # ctp_manager.current_user.query_investor_position_detail(ExchangeType.SZSE.name)




    # print('HO2410的看涨期权的第一个行权价的行权价：{}'.format(ctp_manager.memory.option_manager.index_option_market_data[0, 0, 0, 0]))
    # print('HO2410的看涨期权的第二个行权价的行权价：{}'.format(
    #     ctp_manager.memory.option_manager.index_option_market_data[0, 0, 1, 0]))



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

@app.route('/api/users', methods=['GET'])
def get_users():
    result = []
    for user in ctp_manager.users.values():
        resp = UserResp(user.user_id, user.user_name)
        result.append(resp.to_dict())
    return jsonify(result)

# body:{
#     'user_name': '薛建华'
# }
@app.route('/api/users', methods=['POST'])
def set_user():
    data: Dict[str, str] = request.get_json()
    user_name: str = data.get('user_name')
    ctp_manager.switch_to_user(user_name)
    return jsonify({"message": "Baseline type set successfully", "user_name": user_name}), 200

@app.route('/api/get_all_market_data', methods=['GET'])
def get_all_market_data():
    # 返回当前行情数据
    return None

@app.route('/api/cffex/options', methods=['GET'])
def get_cffex_option():
    if ctp_manager.current_user.memory.option_manager is not None:
        return jsonify(list(ctp_manager.current_user.memory.option_manager.index_future_symbol))
    else:
        return jsonify([])

@app.route('/api/se/options', methods=['GET'])
def get_se_option():
    if ctp_manager.current_user.memory.option_manager is not None:
        return jsonify(list(ctp_manager.current_user.memory.option_manager.etf_option_symbol))
    else:
        return jsonify([])

@app.route('/api/futures', methods=['GET'])
def get_all_future():
    if ctp_manager.current_user.memory.future_manager is not None:
        return jsonify(ctp_manager.current_user.memory.future_manager.index_future_symbol)
    else:
        return jsonify([])

@app.route('/api/option/greeks', methods=['GET'])
def get_option_greeks():
    symbol = request.args.get('symbol')
    print(f"get_cffex_option_greeks: symbol {symbol}")
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404

    resp = OptionGreeksResp(symbol)
    for strike_price, option_tuple in ctp_manager.current_user.memory.option_manager.option_series_dict[symbol].strike_price_options.items():
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


    # print(resp.to_dict())
    return jsonify(resp.to_dict())



@app.route('/api/option/wing_model', methods=['GET'])
def get_wing_model_by_symbol():
    symbol: str = request.args.get('symbol')
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404

    result = [generate_wing_model_response(symbol).to_dict()]

    expired_month = symbol[-8:][:6]
    sh_symbol: str
    cffex_symbol: str
    if filter_etf_option(symbol):
        sh_symbol = symbol
        cffex_instrument = ctp_manager.current_user.memory.option_manager.grouped_instruments[expired_month][0]
        if cffex_instrument is not None:
            cffex_symbol = cffex_instrument.symbol
        else:
            # 处理 cffex_instrument 为 None 的情况
            result.append(generate_wing_model_response(symbol).to_dict())
            return
    elif filter_index_option(symbol):
        sh_instrument = ctp_manager.current_user.memory.option_manager.grouped_instruments[expired_month][1]
        if sh_instrument is not None:
            sh_symbol = sh_instrument.symbol
        else:
            result.append(generate_wing_model_response(symbol).to_dict())
            return
        cffex_symbol = symbol
    else:
        return jsonify({"error": "Unrecognized option type"}), 400

    sh_response = generate_wing_model_response(sh_symbol)
    cffex_response = generate_wing_model_response(cffex_symbol)


    if ctp_manager.baseline == BaselineType.INDIVIDUAL.value:
        result.append(sh_response.to_dict() if filter_etf_option(symbol) else cffex_response.to_dict())
    elif ctp_manager.baseline == BaselineType.AVERAGE.value:

        if sh_response.atm_volatility.atm_valid and cffex_response.atm_volatility.atm_valid == 1:
            baseline_resp: WingModelResp = WingModelResp((sh_response.atm_volatility + cffex_response.atm_volatility) / 2,
                                                         (sh_response.k1 + cffex_response.k1) / 2,
                                                         (sh_response.k2 + cffex_response.k2) / 2,
                                                         (sh_response.b + cffex_response.b) / 2,
                                                         1)
            result.append(baseline_resp.to_dict())
        else:
            result.append(generate_wing_model_response(symbol).to_dict())
    elif ctp_manager.baseline == BaselineType.SH.value:
        result.append(sh_response.to_dict())
    else:
        return jsonify({"error": "Unrecognized baseline type"}), 400

    print(result)

    return jsonify(result)

def generate_wing_model_response(symbol: str) -> WingModelResp:
    option_series = ctp_manager.current_user.memory.option_manager.option_series_dict[symbol]
    wing_model_para: WingModelPara = option_series.wing_model_para
    atm_volatility: ATMVolatility = option_series.atm_volatility
    return WingModelResp(atm_volatility.atm_volatility_protected, wing_model_para.k1, wing_model_para.k2, wing_model_para.b, atm_volatility.atm_valid)

@app.route('/api/option/wing_model', methods=['GET'])
def get_all_customized_wing_model_para():
    resp: Dict[str, WingModelPara] = {}
    if ctp_manager.current_user.memory.option_manager is not None:
        for symbol, option_series in ctp_manager.current_user.memory.option_manager.option_series_dict.items():
            wing_model_para: WingModelPara = option_series.customized_wing_model_para
            resp[symbol] = wing_model_para

    print(f"get_all_customized_wing_model_para: {resp}")
    return jsonify(resp)

@app.route('/api/option/wing_model', methods=['POST'])
def set_customized_wing_model():
    data: Dict[str, dict] = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid or missing JSON data"}), 400
    for symbol, value in data.items():
        # print(f"symbol:{symbol}, value:{value}")
        option_manager = ctp_manager.current_user.memory.option_manager

        if option_manager is not None:
            if "v" in value:
                option_manager.option_series_dict[symbol].customized_wing_model_para.v = value["v"]
            if "k1" in value:
                option_manager.option_series_dict[symbol].customized_wing_model_para.k1 = value["k1"]
            if "k2" in value:
                option_manager.option_series_dict[symbol].customized_wing_model_para.k2 = value["k2"]
            if "b" in value:
                option_manager.option_series_dict[symbol].customized_wing_model_para.b = value["b"]

    return jsonify({"message": "Customized wing model received"}), 200

@app.route('/api/baseline', methods=['POST'])
def set_baseline():
    data = request.get_json()
    baseline_type_str: str = data.get('baseline')
    print(f"set_baseline: {baseline_type_str}")
    if not baseline_type_str:
        return jsonify({"error": "Baseline type not provided"}), 400

    try:
        # 转换字符串到 BaselineType 枚举
        baseline_type = BaselineType[baseline_type_str.upper()]
        ctp_manager.baseline = baseline_type  # 更新当前基准类型
        return jsonify({"message": "Baseline type set successfully", "current_baseline": baseline_type.value}), 200
    except KeyError:
        return jsonify({"error": f"Invalid baseline type: {baseline_type_str}"}), 400

# 获取当前基准类型的接口
@app.route('/api/baseline', methods=['GET'])
def get_baseline():
    return jsonify({"current_baseline": ctp_manager.baseline.name.lower()}), 200


if __name__ == "__main__":
    init_ctp()
    Thread(target=main).start()
    app.run(debug=True, use_reloader=False)


