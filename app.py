import logging
import time
from flask_socketio import SocketIO, emit

import numpy as np
from typing import Dict, List

from helper.helper import filter_index_option, filter_etf_option, filter_index_future, get_cash_multiplier, \
    parse_option_full_symbol
from model.ctp_manager import CTPManager
from model.direction import Direction
from model.enum.baseline_type import BaselineType
from model.enum.category import UNDERLYING_CATEGORY_MAPPING, INDEX_OPTION_ETF_OPTION_FUTURE_MAPPING
from model.enum.exchange_type import ExchangeType
from model.instrument.option_series import OptionSeries
from model.memory.wing_model_para import WingModelPara
from model.response.greeks_total_resp import GreeksTotalResp
from model.response.monitor_total_resp import MonitorTotalResp
from model.response.option_greeks import OptionGreeksData, OptionGreeksResp
from model.response.option_resp_base import StrikePrices
from model.response.greeks_cash_resp import GreeksCashResp
from model.response.user import UserResp
from model.response.wing_model_resp import WingModelResp

np.set_printoptions(suppress=True)
from threading import Thread

from flask import Flask, jsonify, render_template, send_from_directory, request

app = Flask(__name__, static_folder='./frontend/build')
socketio = SocketIO(app, logger=False)

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

ctp_manager = CTPManager('dev')

def init_ctp():
    # 初始化
    global ctp_manager

    for user in ctp_manager.users.keys():
        ctp_manager.switch_to_user(user)
        break

    print(f"合约Id对应full symbol: {ctp_manager.market_data_manager.instrument_transform_full_symbol}")
    print(f"品类分组:")
    for category, group_instrument in ctp_manager.market_data_manager.grouped_instruments.items():
        print(f'{category}: {group_instrument}')
    print('当前订阅期货合约数量为：{}'.format(len(ctp_manager.market_data_manager.index_futures_dict)))
    print('当前订阅期货合约月份为：{}'.format(ctp_manager.market_data_manager.index_future_symbol))


    print('当前订阅期权合约数量为：{}'.format(len(ctp_manager.market_data_manager.option_market_data)))
    print('当前订阅指数期权合约月份为：{}'.format(ctp_manager.market_data_manager.index_option_symbol))
    print('当前订阅ETF期权合约月份为：{}'.format(ctp_manager.market_data_manager.etf_option_symbol))



def main():
    # test_future_instruction("IF2502", "0081500056", 3900, 3800)
    # test_se_instruction("91013096", "9982100962", 0.08, 0.07)

    while True:
        time.sleep(3)

def test_position():
    print(get_se_monitor("HO20250221"))
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX, "HO2502-C-2400", Direction.SELL_OPEN, 200, 4)
    print(get_se_monitor("HO20250221"))
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX, "HO2502-C-2400", Direction.BUY_OPEN, 240, 1)
    print(get_se_monitor("HO20250221"))
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX, "HO2502-C-2400", Direction.BUY_CLOSE, 240, 1)
    print(get_se_monitor("HO20250221"))

def test_future_instruction(instrument_id, investor_id, high, low):
    # 卖开
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX, investor_id, instrument_id, Direction.SELL_OPEN, low, 1)
    # # 买开
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX, investor_id, instrument_id, Direction.BUY_OPEN, high, 1)
    # 买平
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX, investor_id, instrument_id, Direction.BUY_CLOSE, high, 1)
    # # # 卖平
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX, investor_id, instrument_id, Direction.SELL_CLOSE, low, 1)

    # 买撤
    order_ref = ctp_manager.current_user.insert_order(ExchangeType.CFFEX, investor_id, instrument_id, Direction.BUY_OPEN, low, 1)
    ctp_manager.current_user.order_action(ExchangeType.CFFEX, investor_id, instrument_id, order_ref)
    #
    #卖撤
    order_ref = ctp_manager.current_user.insert_order(ExchangeType.CFFEX, investor_id, instrument_id, Direction.SELL_OPEN, high, 1)
    ctp_manager.current_user.order_action(ExchangeType.CFFEX, investor_id, instrument_id, order_ref)

def test_se_instruction(instrument_id, investor_id, high, low):
    # 卖开
    ctp_manager.current_user.insert_order(ExchangeType.SE, investor_id, instrument_id, Direction.SELL_OPEN, low, 1)
    # 买开
    ctp_manager.current_user.insert_order(ExchangeType.SE, investor_id, instrument_id, Direction.BUY_OPEN, high, 1)
    # 买平
    ctp_manager.current_user.insert_order(ExchangeType.SE, investor_id, instrument_id, Direction.BUY_CLOSE, high, 1)
    # 卖平
    ctp_manager.current_user.insert_order(ExchangeType.SE, investor_id, instrument_id, Direction.SELL_CLOSE, low, 1)

    # 买撤
    order_ref = ctp_manager.current_user.insert_order(ExchangeType.SE, investor_id, instrument_id, Direction.BUY_OPEN, low, 1)
    ctp_manager.current_user.order_action(ExchangeType.SE, investor_id, instrument_id, order_ref)
    #
    #卖撤
    order_ref = ctp_manager.current_user.insert_order(ExchangeType.SE, investor_id, instrument_id, Direction.SELL_OPEN, high, 1)
    ctp_manager.current_user.order_action(ExchangeType.SE, investor_id, instrument_id, order_ref)

def test_instruction():
    # 卖开
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX, "HO2502-C-2400", Direction.SELL_OPEN, 180, 1)
    # # 买开
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX, "HO2502-C-2500", Direction.BUY_OPEN, 230, 1)
    # 买平
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX, "HO2502-C-2400", Direction.BUY_CLOSE, 230, 1)
    # # # 卖平
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX, "HO2502-C-2400", Direction.SELL_CLOSE, 180, 1)

    # 买撤
    order_ref = ctp_manager.current_user.insert_order(ExchangeType.CFFEX, "HO2502-C-2400", Direction.BUY_OPEN, 180, 1)
    ctp_manager.current_user.order_action(ExchangeType.CFFEX, "HO2502-C-2400", order_ref)
    #
    #卖撤
    order_ref = ctp_manager.current_user.insert_order(ExchangeType.CFFEX, "HO2502-C-2400", Direction.SELL_OPEN, 230, 1)
    ctp_manager.current_user.order_action(ExchangeType.CFFEX, "HO2502-C-2400", order_ref)


def test():
    ctp_manager.switch_to_user("Zhuang")
    ctp_manager.current_user.insert_order(ExchangeType.CFFEX, "HO2412-C-2400", Direction.BUY_OPEN, 285, 40)

    order_ref = ctp_manager.current_user.insert_order(ExchangeType.CFFEX, "au2502", Direction.BUY_OPEN, 270, 1)
    if order_ref is not None:
        ctp_manager.current_user.order_action(ExchangeType.CFFEX, "au2502", order_ref)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clock', methods=['GET'])
def get_clock():
    return jsonify(ctp_manager.market_data_manager.clock)

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
    if ctp_manager.market_data_manager is not None:
        return jsonify(list(ctp_manager.market_data_manager.index_option_symbol))
    else:
        return jsonify([])

@app.route('/api/se/options', methods=['GET'])
def get_se_option():
    if ctp_manager.market_data_manager is not None:
        return jsonify(list(ctp_manager.market_data_manager.etf_option_symbol))
    else:
        return jsonify([])

@app.route('/api/futures', methods=['GET'])
def get_all_future():
    if ctp_manager.market_data_manager is not None:
        return jsonify(ctp_manager.market_data_manager.index_future_symbol)
    else:
        return jsonify([])

@app.route('/api/option/greeks', methods=['GET'])
def get_option_greeks():
    symbol = request.args.get('symbol')
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404

    resp = OptionGreeksResp(symbol)
    combined_positions = ctp_manager.current_user.user_memory.get_combined_position()

    for strike_price, option_tuple in ctp_manager.market_data_manager.option_market_data[symbol].strike_price_options.items():
        call_delta = option_tuple.call.greeks.delta
        put_delta = option_tuple.put.greeks.delta
        gamma = option_tuple.call.greeks.gamma
        vega = option_tuple.call.greeks.vega
        call_theta = option_tuple.call.greeks.theta
        put_theta = option_tuple.put.greeks.theta
        vanna_vs = option_tuple.call.greeks.vanna_vs
        vanna_sv = option_tuple.call.greeks.vanna_sv
        db = option_tuple.call.greeks.db
        dkurt = (option_tuple.call.greeks.dk1 + option_tuple.call.greeks.dk2) / 2

        net_position = 0
        if ctp_manager.current_user is not None and option_tuple.call.full_symbol in combined_positions:
            position = combined_positions[option_tuple.call.full_symbol]
            net_position = position.long - position.short

        call_option = OptionGreeksData(call_delta, gamma, vega, call_theta, vanna_vs=vanna_vs, vanna_sv=vanna_sv, db=db, dkurt=dkurt, position=net_position, ask=option_tuple.call.market_data.ask_prices[0], bid=option_tuple.call.market_data.bid_prices[0])

        net_position = 0
        if ctp_manager.current_user is not None and option_tuple.put.full_symbol in combined_positions:
            position = combined_positions[option_tuple.put.full_symbol]
            net_position = position.long - position.short

        put_option = OptionGreeksData(put_delta, gamma, vega, put_theta, vanna_vs=vanna_vs, vanna_sv=vanna_sv, db=db, dkurt=dkurt, position=net_position, ask=option_tuple.put.market_data.ask_prices[0], bid=option_tuple.put.market_data.bid_prices[0])
        resp.strike_prices[strike_price] = StrikePrices(call_option, put_option)

    return jsonify(resp.to_dict())



@app.route('/api/option/wing_model/', methods=['GET'])
def get_wing_model_by_symbol():
    symbol: str = request.args.get('symbol')
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404

    result = [generate_wing_model_response(symbol).to_dict()]

    group_instrument = ctp_manager.market_data_manager.get_group_instrument_by_symbol(symbol)
    if group_instrument is None:
        # 深交所的
        result.append(generate_wing_model_response(symbol).to_dict())
        return result

    sh_symbol: str
    cffex_symbol: str
    if filter_etf_option(symbol):
        sh_symbol = symbol
        if group_instrument.index_option_series is not None:
            cffex_symbol = group_instrument.index_option_series.symbol
        else:
            # 处理 cffex_instrument 为 None 的情况
            result.append(generate_wing_model_response(symbol).to_dict())
            return result
    elif filter_index_option(symbol):
        if group_instrument.etf_option_series is not None:
            sh_symbol = group_instrument.etf_option_series.symbol
        else:
            result.append(generate_wing_model_response(symbol).to_dict())
            return result
        cffex_symbol = symbol
    else:
        return jsonify({"error": f"Unrecognized option type {symbol}"}), 400

    sh_response = generate_wing_model_response(sh_symbol)
    cffex_response = generate_wing_model_response(cffex_symbol)


    if ctp_manager.market_data_manager.baseline == BaselineType.INDIVIDUAL:
        result.append(sh_response.to_dict() if filter_etf_option(symbol) else cffex_response.to_dict())
    elif ctp_manager.market_data_manager.baseline == BaselineType.AVERAGE:

        if sh_response.atm_available and cffex_response.atm_available:
            baseline_resp: WingModelResp = WingModelResp((sh_response.atm_volatility + cffex_response.atm_volatility) / 2,
                                                         (sh_response.k1 + cffex_response.k1) / 2,
                                                         (sh_response.k2 + cffex_response.k2) / 2,
                                                         (sh_response.b + cffex_response.b) / 2,
                                                         1)
            result.append(baseline_resp.to_dict())
        else:
            result.append(generate_wing_model_response(symbol).to_dict())
    elif ctp_manager.market_data_manager.baseline == BaselineType.SH:
        result.append(sh_response.to_dict())
    else:
        return jsonify({"error": "Unrecognized baseline type"}), 400

    return jsonify(result)
    # return result

@app.route('/api/option/wing_models', methods=['GET'])
def get_all_customized_wing_model_para():
    resp: Dict[str, WingModelPara] = {}
    if ctp_manager.market_data_manager is not None:
        for symbol, option_series in ctp_manager.market_data_manager.option_market_data.items():
            wing_model_para: WingModelPara = option_series.customized_wing_model_para
            resp[symbol] = wing_model_para

    return jsonify(resp)

@app.route('/api/option/wing_models', methods=['POST'])
def set_customized_wing_model():
    data: Dict[str, dict] = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid or missing JSON data"}), 400
    for symbol, value in data.items():
        if ctp_manager.market_data_manager is not None:
            if "v" in value:
                ctp_manager.market_data_manager.option_market_data[symbol].customized_wing_model_para.v = float(value["v"])
            if "k1" in value:
                ctp_manager.market_data_manager.option_market_data[symbol].customized_wing_model_para.k1 = float(value["k1"])
            if "k2" in value:
                ctp_manager.market_data_manager.option_market_data[symbol].customized_wing_model_para.k2 = float(value["k2"])
            if "b" in value:
                ctp_manager.market_data_manager.option_market_data[symbol].customized_wing_model_para.b = float(value["b"])

    return jsonify({"message": "Customized wing model received"}), 200

@app.route('/api/baseline', methods=['POST'])
def set_baseline():
    data = request.get_json()
    baseline_type_str: str = data.get('baseline')

    if not baseline_type_str:
        return jsonify({"error": "Baseline type not provided"}), 400

    try:
        # 转换字符串到 BaselineType 枚举
        baseline_type = BaselineType[baseline_type_str.upper()]
        ctp_manager.market_data_manager.baseline = baseline_type  # 更新当前基准类型
        return jsonify({"message": "Baseline type set successfully", "current_baseline": baseline_type.value}), 200
    except KeyError:
        return jsonify({"error": f"Invalid baseline type: {baseline_type_str}"}), 400

# 获取当前基准类型的接口
@app.route('/api/baseline', methods=['GET'])
def get_baseline():
    return jsonify(ctp_manager.market_data_manager.baseline.name.lower())

@app.route('/api/option/greeks_summary', methods=['GET'])
def get_greek_summary_by_option_symbol():
    if ctp_manager.current_user is None:
        return jsonify({"error": f"error not set user"}), 404

    symbol: str = request.args.get('symbol')
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404

    # Convert each data instance to a dictionary and return as JSON
    return jsonify(get_option_position_greeks(symbol, ctp_manager.current_user.user_name).to_dict())

@app.route('/api/future/greeks_summary', methods=['GET'])
def get_greek_summary_by_future_symbol():
    if ctp_manager.current_user is None:
        return jsonify({"error": f"error not set user"}), 404

    symbol: str = request.args.get('symbol')
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404

    group_instrument = ctp_manager.market_data_manager.get_group_instrument_by_symbol(symbol)

    if group_instrument is not None and group_instrument.future is not None:
        # Convert each data instance to a dictionary and return as JSON
        return jsonify(position_greeks.to_dict() for position_greeks in get_future_position_greeks(group_instrument.future.symbol, ctp_manager.current_user.user_name))
    else:
        return jsonify([])

def get_future_position_greeks(symbol: str, user_name: str):
    future = ctp_manager.market_data_manager.index_futures_dict[symbol]

    cash_multiplier = get_cash_multiplier(symbol)

    underlying_price = (future.market_data.bid_prices[0] + future.market_data.ask_prices[0]) / 2

    user = ctp_manager.users[user_name]

    result = []
    for investor_id, positions in user.user_memory.positions.items():
        if user.investors[investor_id] == ExchangeType.CFFEX:
            if symbol in positions:
                future_position = positions[symbol]
                delta = future_position.long - future_position.short
                delta_cash = delta * cash_multiplier * underlying_price
                result.append(GreeksCashResp(investor_id=investor_id, delta=delta, delta_cash=delta_cash, underlying_price=underlying_price))
            else:
                result.append(GreeksCashResp(investor_id=investor_id, underlying_price=underlying_price))

    return result


def get_option_position_greeks(symbol: str, user_name: str):
    option_series: OptionSeries = ctp_manager.market_data_manager.option_market_data[symbol]

    delta = 0
    gamma = 0
    vega = 0
    theta = 0
    db = 0
    charm = 0
    vanna_vs = 0
    vanna_sv = 0
    dkurt = 0
    cash_multiplier = get_cash_multiplier(symbol)

    user = ctp_manager.users.get(user_name, ctp_manager.current_user)

    positions = user.user_memory.get_combined_position()

    for full_symbol, position in positions.items():
        if not full_symbol.startswith(symbol):
            continue

        symbol, option_type, strike_price = parse_option_full_symbol(full_symbol)
        underlying_option = ctp_manager.market_data_manager.option_market_data[symbol].get_option(strike_price, option_type)
        multiple = underlying_option.underlying_multiple * (position.long - position.short)
        delta += underlying_option.greeks.delta * multiple
        gamma += underlying_option.greeks.gamma * multiple
        vega += underlying_option.greeks.vega * multiple
        theta += underlying_option.greeks.theta * multiple
        db += underlying_option.greeks.db * multiple
        charm += underlying_option.greeks.charm * multiple
        vanna_vs += underlying_option.greeks.vanna_vs * multiple
        vanna_sv += underlying_option.greeks.vanna_sv * multiple
        dkurt += (underlying_option.greeks.dk1 + underlying_option.greeks.dk2) / 2 * multiple

    delta_cash = delta * option_series.wing_model_para.S * cash_multiplier
    gamma_cash = gamma * option_series.wing_model_para.S * cash_multiplier
    vega_cash = vega * cash_multiplier
    theta_cash = theta * cash_multiplier
    db_cash = db * cash_multiplier
    charm_cash = charm * option_series.wing_model_para.S * cash_multiplier
    vanna_vs_cash = vanna_vs * cash_multiplier
    vanna_sv_cash = vanna_sv * option_series.wing_model_para.S * cash_multiplier
    dkurt_cash = dkurt * cash_multiplier

    resp: GreeksCashResp = GreeksCashResp(delta=delta, delta_cash=delta_cash, gamma_p_cash=gamma_cash, vega_cash=vega_cash, theta_cash=theta_cash, db_cash=db_cash, charm_cash=charm_cash, vanna_sv_cash=vanna_sv_cash, vanna_vs_cash=vanna_vs_cash, dkurt_cash=dkurt_cash, underlying_price=option_series.wing_model_para.S)

    return resp




def generate_wing_model_response(symbol: str) -> WingModelResp:
    option_series = ctp_manager.market_data_manager.option_market_data[symbol]

    if option_series.customized_wing_model_para.v == 0:
        wing_model_para = option_series.wing_model_para
        return WingModelResp(option_series.atm_volatility.atm_volatility_protected, wing_model_para.k1, wing_model_para.k2, wing_model_para.b, option_series.atm_volatility.atm_valid)
    else:
        wing_model_para = option_series.customized_wing_model_para
        return WingModelResp(wing_model_para.v, wing_model_para.k1, wing_model_para.k2, wing_model_para.b, option_series.atm_volatility.atm_valid)

@app.route('/api/cffex/monitor', methods=['GET'])
def get_cffex_monitor():
    if ctp_manager is None or ctp_manager.current_user is None:
        return jsonify({"error": f"ctp manager exception"}), 404

    symbol: str = request.args.get('symbol')
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404

    combined_position = ctp_manager.current_user.user_memory.get_combined_position()

    result : int = 0
    for full_symbol, position in combined_position.items():
        if full_symbol.startswith(symbol):
            result += position.short_open_volume + position.long_open_volume
    return jsonify(str(result))

@app.route('/api/se/monitor', methods=['GET'])
def get_se_monitor():
    if ctp_manager is None or ctp_manager.current_user is None:
        return jsonify({"error": f"ctp manager exception"}), 404

    symbol: str = request.args.get('symbol')
    if symbol is None or symbol == "":
        return jsonify({"error": f"Symbol invalid"}), 404


    result = calculate_monitor_index(ctp_manager.current_user.user_name, symbol)
    return jsonify(result)

def calculate_monitor_index(user_name: str, symbol: str):
    net_position: int = 0
    total_amount: int = 0
    combined_position = ctp_manager.users.get(user_name, ctp_manager.current_user).user_memory.get_combined_position()

    for full_symbol, position in combined_position.items():
        if full_symbol.startswith(symbol[:-8]):
            net_position += abs(position.long - position.short)
            total_amount += position.short_open_volume + position.long_open_volume + position.short_close_volume + position.long_close_volume

    if net_position == 0:
        result = str(net_position) + "#" + str(total_amount)
    else:
        result = str(net_position) + "#" + str(total_amount) + "#" + f"{round((total_amount / net_position) * 100, 2)}%"

    return result



@app.route('/api/greeks/total', methods=['GET'])
def get_greeks_total():
    resp = []
    for user_name, user in ctp_manager.users.items():
        greeks_total = GreeksTotalResp(user_name)
        for category, (index_option_prefix_symbol, etf_option_prefix_symbol, future_prefix_symbol) in INDEX_OPTION_ETF_OPTION_FUTURE_MAPPING.items():
            position_greeks = GreeksCashResp()

            for index_option_symbol in ctp_manager.market_data_manager.index_option_symbol:
                if index_option_prefix_symbol is not None and index_option_symbol.startswith(index_option_prefix_symbol):
                    position_greeks += get_option_position_greeks(index_option_symbol, user_name)

            for etf_option_symbol in ctp_manager.market_data_manager.etf_option_symbol:
                if etf_option_prefix_symbol is not None and etf_option_symbol.startswith(etf_option_prefix_symbol):
                    position_greeks += get_option_position_greeks(etf_option_symbol, user_name)

            for index_future_symbol in ctp_manager.market_data_manager.index_future_symbol:
                if future_prefix_symbol is not None and index_future_symbol.startswith(future_prefix_symbol):
                    for future_greeks in get_future_position_greeks(index_future_symbol, user_name):
                        position_greeks += future_greeks

            greeks_total.greeks_total_by_category[category] = {
                "delta_cash": position_greeks.delta_cash,
                "vega_cash": position_greeks.vega_cash,
                "theta_cash": position_greeks.theta_cash,
                "gamma_p_cash": position_greeks.gamma_p_cash,
                "db_cash": position_greeks.db_cash,
                "vanna_sv_cash": position_greeks.vanna_sv_cash,
                "vanna_vs_cash": position_greeks.vanna_vs_cash,
                "dkurt_cash": position_greeks.dkurt_cash
            }

        resp.append(greeks_total.to_dict())

    return jsonify(resp)

@app.route('/api/monitor/total', methods=['GET'])
def get_monitor_total():
    resp = []
    for user_name, user in ctp_manager.users.items():
        monitor_total = MonitorTotalResp(user_name)
        symbols = ["510050", "510300", "510500"]
        for symbol in symbols:
            monitor_total.monitor_total_by_category[UNDERLYING_CATEGORY_MAPPING[symbol]] = calculate_monitor_index(user_name, symbol)
        resp.append(monitor_total.to_dict())
    return jsonify(resp)


if __name__ == "__main__":
    init_ctp()
    Thread(target=main).start()
    app.run(debug=True, use_reloader=False, port=5002)


