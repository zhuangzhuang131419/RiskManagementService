import time
from dataclasses import asdict

import numpy as np
from typing import Dict

from helper.helper import filter_index_option, filter_etf_option, filter_index_future, get_cash_multiplier, \
    parse_option_full_symbol
from model.ctp_manager import CTPManager
from model.direction import Direction
from model.enum.baseline_type import BaselineType
from model.enum.category import UNDERLYING_CATEGORY_MAPPING
from model.enum.exchange_type import ExchangeType
from model.instrument.option import Option
from model.instrument.option_series import OptionSeries
from model.memory.atm_volatility import ATMVolatility
from model.memory.wing_model_para import WingModelPara
from model.response.option_greeks import OptionGreeksData, OptionGreeksResp
from model.response.option_resp_base import StrikePrices
from model.response.greeks_cash_resp import GreeksCashResp
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

    # ctp_manager.current_user.insert_order(ExchangeType.CFFEX, "HO2412-C-2400", Direction.BUY_OPEN, 335, 1)
    # time.sleep(10)



    # time.sleep(10)

    # ctp_manager.current_user.query_investor_position(ExchangeType.CFFEX.name)
    # time.sleep(10)
    # # ctp_manager.current_user.insert_order(ExchangeType.CFFEX.name, "HO2412-C-2400", Direction.SELL_CLOSE, 285, 1)
    # time.sleep(10)
    # ctp_manager.current_user.query_investor_position(ExchangeType.CFFEX.name)
    # time.sleep(10)
    # # ctp_manager.current_user.insert_order(ExchangeType.CFFEX.name, "HO2412-C-2400", Direction.SELL_OPEN, 285, 1)
    # time.sleep(10)
    # ctp_manager.current_user.query_investor_position(ExchangeType.CFFEX.name)
    # time.sleep(10)
    # # ctp_manager.current_user.insert_order(ExchangeType.CFFEX.name, "HO2412-C-2400", Direction.BUY_CLOSE, 295, 1)
    # time.sleep(10)
    # ctp_manager.current_user.query_investor_position(ExchangeType.CFFEX.name)

    # ctp_manager.current_user.insert_order(ExchangeType.SE.name, "10007328", Direction.SELL_CLOSE, 0.10, 3)
    # ctp_manager.current_user.insert_order(ExchangeType.SE.name, "10007328", Direction.SELL_OPEN, 0.10, 4)

    # ctp_manager.current_user.query_investor_position_detail(ExchangeType.SE.name)
    # ctp_manager.current_user.insert_order(ExchangeType.SE.name, "10007328", Direction.BUY_OPEN, 0.12, 2)
    # time.sleep(10)


    # ctp_manager.current_user.insert_order(ExchangeType.SE.name, "10007328", Direction.BUY_CLOSE, 0.12, 4)
    # time.sleep(10)
    # ctp_manager.current_user.insert_order(ExchangeType.CFFEX.name, "HO2412-C-2400", Direction.SELL_CLOSE, 280, 1)
    # ctp_manager.current_user.query_investor_position(ExchangeType.SE.name)


    print(f"合约Id对应full symbol: {ctp_manager.market_data_manager.instrument_transform_full_symbol}")
    print(f"品类分组: {ctp_manager.market_data_manager.grouped_instruments}")
    print('当前订阅期货合约数量为：{}'.format(len(ctp_manager.market_data_manager.index_futures_dict)))
    print('当前订阅期货合约月份为：{}'.format(ctp_manager.market_data_manager.index_future_symbol))


    print('当前订阅期权合约数量为：{}'.format(len(ctp_manager.market_data_manager.option_market_data)))
    print('当前订阅指数期权合约月份为：{}'.format(ctp_manager.market_data_manager.index_option_symbol))
    print('当前订阅ETF期权合约月份为：{}'.format(ctp_manager.market_data_manager.etf_option_symbol))


    # if ctp_manager.current_user is not None:
    #     ctp_manager.current_user.query_investor_position(ExchangeType.SE, None, 20)
    # if ctp_manager.current_user is not None:
    #     ctp_manager.current_user.query_investor_position(ExchangeType.CFFEX, None, 20)

    Thread(target=ctp_manager.current_user.market_data_memory.index_volatility_calculator).start()

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
        print(f"HO20241115: {get_wing_model_by_symbol('MO20241220')}")
        # print(f"51030020241225: {get_wing_model_by_symbol('51030020241225')}")
        time.sleep(3)


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
    if ctp_manager.current_user.market_data_memory is not None:
        return jsonify(list(ctp_manager.current_user.market_data_memory.index_option_symbol))
    else:
        return jsonify([])

@app.route('/api/se/options', methods=['GET'])
def get_se_option():
    if ctp_manager.current_user.market_data_memory is not None:
        return jsonify(list(ctp_manager.current_user.market_data_memory.etf_option_symbol))
    else:
        return jsonify([])

@app.route('/api/futures', methods=['GET'])
def get_all_future():
    if ctp_manager.current_user.market_data_memory is not None:
        return jsonify(ctp_manager.current_user.market_data_memory.index_future_symbol)
    else:
        return jsonify([])

@app.route('/api/option/greeks', methods=['GET'])
def get_option_greeks():
    symbol = request.args.get('symbol')
    # print(f"get_cffex_option_greeks: symbol {symbol}")
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404

    resp = OptionGreeksResp(symbol)
    for strike_price, option_tuple in ctp_manager.current_user.market_data_memory.option_market_data[symbol].strike_price_options.items():
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



# @app.route('/api/option/wing_model/', methods=['GET'])
def get_wing_model_by_symbol(symbol):
    # symbol: str = request.args.get('symbol')
    print(f"get_wing_model_by_symbol: {symbol}")
    # if symbol is None or symbol == "":
    #     return get_all_customized_wing_model_para()

    result = [generate_wing_model_response(symbol).to_dict()]

    expired_month = symbol[-8:][:6]
    underlying_id = symbol[:-8]
    category = UNDERLYING_CATEGORY_MAPPING[underlying_id].value
    sh_symbol: str
    cffex_symbol: str
    if filter_etf_option(symbol):
        sh_symbol = symbol
        cffex_instrument = ctp_manager.current_user.market_data_memory.grouped_instruments[category + "-" + expired_month].index_option_tuple.call
        if cffex_instrument is not None:
            cffex_symbol = cffex_instrument.symbol
        else:
            # 处理 cffex_instrument 为 None 的情况
            result.append(generate_wing_model_response(symbol).to_dict())
            return result
        print(f"symbol:{symbol}, se symbol:{sh_symbol}, cffex symbol: {cffex_symbol}")
    elif filter_index_option(symbol):
        sh_instrument = ctp_manager.current_user.market_data_memory.grouped_instruments[category + "-" + expired_month].etf_option_tuple.call
        if sh_instrument is not None:
            sh_symbol = sh_instrument.symbol
        else:
            result.append(generate_wing_model_response(symbol).to_dict())
            return result
        cffex_symbol = symbol
        print(f"symbol:{symbol}, se symbol:{sh_symbol}, cffex symbol: {cffex_symbol}")
    else:
        print(f"Invalid {symbol}")
        return jsonify({"error": "Unrecognized option type"}), 400

    sh_response = generate_wing_model_response(sh_symbol)
    cffex_response = generate_wing_model_response(cffex_symbol)


    if ctp_manager.baseline == BaselineType.INDIVIDUAL:
        result.append(sh_response.to_dict() if filter_etf_option(symbol) else cffex_response.to_dict())
    elif ctp_manager.baseline == BaselineType.AVERAGE:

        if sh_response.atm_available and cffex_response.atm_available:
            baseline_resp: WingModelResp = WingModelResp((sh_response.atm_volatility + cffex_response.atm_volatility) / 2,
                                                         (sh_response.k1 + cffex_response.k1) / 2,
                                                         (sh_response.k2 + cffex_response.k2) / 2,
                                                         (sh_response.b + cffex_response.b) / 2,
                                                         1)
            result.append(baseline_resp.to_dict())
        else:
            result.append(generate_wing_model_response(symbol).to_dict())
    elif ctp_manager.baseline == BaselineType.SH:
        result.append(sh_response.to_dict())
    else:
        print(f"baseline:{ctp_manager.baseline}")
        return jsonify({"error": "Unrecognized baseline type"}), 400

    # return jsonify(result)
    return result

def get_all_customized_wing_model_para():
    resp: Dict[str, WingModelPara] = {}
    if ctp_manager.current_user.market_data_memory is not None:
        for symbol, option_series in ctp_manager.current_user.market_data_memory.option_market_data.items():
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
        if ctp_manager.current_user.market_data_memory is not None:
            if "v" in value:
                ctp_manager.current_user.market_data_memory.option_market_data[symbol].customized_wing_model_para.v = value["v"]
            if "k1" in value:
                ctp_manager.current_user.market_data_memory.option_market_data[symbol].customized_wing_model_para.k1 = value["k1"]
            if "k2" in value:
                ctp_manager.current_user.market_data_memory.option_market_data[symbol].customized_wing_model_para.k2 = value["k2"]
            if "b" in value:
                ctp_manager.current_user.market_data_memory.option_market_data[symbol].customized_wing_model_para.b = value["b"]

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

@app.route('/api/position/', methods=['GET'])
def get_position():
    symbol: str = request.args.get('symbol')
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404
    if filter_etf_option(symbol):
        if ctp_manager.current_user.query_investor_position(ExchangeType.SE, None):
            pass
        else:
            return jsonify({"error": f"Timeout"}), 404
    elif filter_index_option(symbol):
        if ctp_manager.current_user.query_investor_position(ExchangeType.CFFEX, None):
            # return
            pass
        else:
            return jsonify({"error": f"Timeout"}), 404
    else:
        return jsonify({"error": f"Symbol invalid"}), 404

@app.route('/api/cash/greeks', methods=['GET'])
def get_greek_summary():
    symbol: str = request.args.get('symbol')
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404
    # Convert each data instance to a dictionary and return as JSON
    return jsonify(get_position_greeks(symbol).to_dict())


def get_position_greeks(symbol: str):

    expired_month = symbol[-8:][:6]
    underlying_id = symbol[:2]
    category = UNDERLYING_CATEGORY_MAPPING[underlying_id].value
    if filter_index_future(symbol):
        return jsonify({"error": f"Symbol invalid"}), 404

    grouped_instrument = ctp_manager.current_user.market_data_memory.grouped_instruments[category + "-" + expired_month]
    if filter_etf_option(symbol) and grouped_instrument.index_option_tuple is None:
        return

    option_series: OptionSeries = ctp_manager.current_user.market_data_memory.option_market_data[symbol]

    delta = 0
    gamma = 0
    vega = 0
    db = 0
    charm = 0
    vanna_vs = 0
    vanna_sv = 0
    dkurt = 0
    cash_multiplier = get_cash_multiplier(symbol)



    for full_symbol, position in ctp_manager.current_user.user_memory.position.items():
        if not full_symbol.startswith(symbol):
            continue
        symbol, option_type, strike_price = parse_option_full_symbol(full_symbol)
        underlying_option = ctp_manager.market_data_manager.option_market_data[symbol].get_option(strike_price, option_type)
        delta += underlying_option.greeks.delta * underlying_option.volume_multiple * (position.long - position.short)
        gamma += underlying_option.greeks.gamma * underlying_option.volume_multiple * (position.long - position.short)
        vega += underlying_option.greeks.vega * underlying_option.volume_multiple *  (position.long - position.short)
        db += underlying_option.greeks.db * underlying_option.volume_multiple * (position.long - position.short)
        charm += underlying_option.greeks.charm * underlying_option.volume_multiple *  (position.long - position.short)
        vanna_vs += underlying_option.greeks.vanna_vs * underlying_option.volume_multiple *  (position.long - position.short)
        vanna_sv += underlying_option.greeks.vanna_sv * underlying_option.volume_multiple *  (position.long - position.short)
        dkurt += (underlying_option.greeks.dk1 + underlying_option.greeks.dk2) / 2 * underlying_option.volume_multiple *  (position.long - position.short)

    delta_cash = delta * option_series.wing_model_para.S * cash_multiplier
    gamma_cash = gamma * option_series.wing_model_para.S * cash_multiplier
    vega_cash = vega * cash_multiplier
    db_cash = db * cash_multiplier
    charm_cash = charm * cash_multiplier
    vanna_vs_cash = vanna_vs * cash_multiplier
    vanna_sv_cash = vanna_sv * cash_multiplier
    dkurt_cash = dkurt * cash_multiplier

    resp: GreeksCashResp = GreeksCashResp(delta=delta, delta_cash=delta_cash, gamma_p_cash=gamma_cash, vega_cash=vega_cash, db_cash=db_cash, charm_cash=charm_cash, vanna_sv_cash=vanna_sv_cash, vanna_vs_cash=vanna_vs_cash, dkurt_cash=dkurt_cash)

    return resp




def generate_wing_model_response(symbol: str) -> WingModelResp:
    option_series = ctp_manager.market_data_manager.option_market_data[symbol]
    wing_model_para: WingModelPara = option_series.wing_model_para
    atm_volatility: ATMVolatility = option_series.atm_volatility
    return WingModelResp(atm_volatility.atm_volatility_protected, wing_model_para.k1, wing_model_para.k2, wing_model_para.b, atm_volatility.atm_valid)


if __name__ == "__main__":
    init_ctp()
    Thread(target=main).start()
    app.run(debug=True, use_reloader=False)


