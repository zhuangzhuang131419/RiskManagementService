import datetime

from model.instrument.option import validate_option_id


# 判断发送请求失败原因
def judge_ret(ret):
    if ret == -1:
        print('失败原因：网络连接失败')
    elif ret == -2:
        print('失败原因：表示未处理请求超过许可数')
    elif ret == -3:
        print('失败原因：表示每秒发送请求数超过许可数')
    else:
        print('失败原因：未知。\nret：{}'.format(ret))

def red_print(content):
    print(f'\033[0;0;31m{content}\033[0m')


# 指数期货的品种列表
INDEX_FUTURE_PREFIXES = ['IH', 'IF', 'IM']
# 指数期权的品种列表
INDEX_OPTION_PREFIXES = ['HO', 'IO', 'MO']
# ETF的品种列表
ETF_PREFIXES = ['510050', '510300', '510500', '159919', '159901']


OPTION_PUT_CALL_DICT = {'C': 0, 'P': 1}

INTEREST_RATE = 0.025
DIVIDEND = 0
TIMEOUT = 15

def filter_index_future(instrument_id: str) -> bool:
    """
    :param instrument_id: 合约id
    :return: 是否是指数期货
    """
    return any(instrument_id.startswith(future_prefix) for future_prefix in INDEX_FUTURE_PREFIXES)

# 判断合约是不是在option
def filter_index_option(symbol: str) -> bool:
    """
    :param symbol: 合约id
    :return: 是否是指数期权
    """
    return any(symbol.startswith(option_prefix) for option_prefix in INDEX_OPTION_PREFIXES)

def filter_etf(symbol: str) -> bool:
    """
    :param symbol: 合约id
    :return: 是否是关注的期权
    """
    return any(symbol.startswith(etf_prefix) for etf_prefix in ETF_PREFIXES)


YEAR_TRADING_DAY=244
#预定义到期时间组
HOLIDAYS=['2024-09-15','2024-09-15','2024-09-17','2024-10-01','2024-10-02','2024-10-03','2024-10-04','2024-10-05',
               '2024-10-06','2024-10-07','2024-12-30','2024-12-31','2025-01-01','2025-02-09','2025-02-10','2025-02-11',
               '2025-02-12','2025-02-13','2025-02-14','2025-02-15','2025-02-16','2025-04-04','2025-05-01','2025-05-02',
               '2025-05-03','2025-05-04','2025-05-05','2025-06-08','2025-06-09','2025-06-10',]

def count_trading_days(start_date, end_date, holidays_list) -> int:
    """
    计算日期间剩余交易日模块；计算日期间剩余周末模块
    :param start_date:
    :param end_date:
    :param holidays_list:
    :return:
    """
    working_days = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # 只计算工作日（周一到周五）
            if current_date.strftime("%Y-%m-%d") not in holidays_list:  # 只计算非假日
                working_days += 1
        current_date += datetime.timedelta(days=1)
    return working_days

def count_sundays(start_date, end_date):
    """
    :param start_date:
    :param end_date:
    :return: 星期天的数量
    """
    sundays = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() == 6:  # 周一是0，周日是6
            sundays += 1
        current_date += datetime.timedelta(days=1)
    return sundays

if __name__ == '__main__':
    print(f'2503-P-4400:{filter_index_option("2503-P-4400")}')
    print(f'2503-P-4400:{filter_index_future("2503-P-4400")}')
    print(f'2412-C-3800:{filter_index_future("2412-C-3800")}')
    print(f'2412-C-3800:{filter_index_option("2412-C-3800")}')
    print(validate_option_id("HO2412-C-3800"))
    print(f'HO2412-C-3800:{filter_index_option("HO2412-C-3800")}')
