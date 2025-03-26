import datetime
from model.enum.category import UNDERLYING_CATEGORY_MAPPING
from model.enum.option_type import OptionType
from utils.logger import Logger


logger = Logger(__name__).logger

# 判断发送请求失败原因
def judge_ret(ret):
    if ret == -1:
        logger.error('失败原因：网络连接失败')
    elif ret == -2:
        logger.error('失败原因：表示未处理请求超过许可数')
    elif ret == -3:
        logger.error('失败原因：表示每秒发送请求数超过许可数')
    else:
        logger.error('失败原因：未知。\nret：{}'.format(ret))

CASH_MULTIPLIER = {
    'HO': 100,
    'MO': 100,
    'IO': 100,
}

# 指数期货的品种列表
INDEX_FUTURE_PREFIXES = ['IH', 'IF', 'IM', 'IC']
# 指数期权的品种列表
INDEX_OPTION_PREFIXES = ['HO', 'IO', 'MO']
# ETF的品种列表
ETF_PREFIXES = ['510050', '510300', '510500', '159919', '159901']


INTEREST_RATE = 0.025
DIVIDEND = 0
TIMEOUT = 15

def get_cash_multiplier(symbol: str) -> int:
    if filter_index_option(symbol):
        return 100
    if filter_etf_option(symbol):
        return 1
    if any(symbol.startswith(prefix) for prefix in ['IF', 'IH']):
        return 300

    if any(symbol.startswith(prefix) for prefix in ['IC', 'IM']):
        return 200

    raise ValueError(f"Invalid symbol:{symbol}")

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

def filter_etf_option(symbol: str) -> bool:
    """
    :param symbol: 合约id
    :return: 是否是关注的期权
    """
    return any(symbol.startswith(etf_prefix) for etf_prefix in ETF_PREFIXES)

def parse_option_full_symbol(full_symbol: str) -> (str, OptionType, float):
    result = full_symbol.split('-')
    # Check if the split result has exactly 3 parts
    if len(result) != 3:
        raise ValueError(f"Invalid format for full_symbol: {full_symbol}. Expected format: 'SYMBOL-TYPE-STRIKE'.")

    # Extract and validate each component
    symbol = result[0]
    option_type_str = result[1]
    strike_price_str = result[2]

    # Validate option type
    if option_type_str not in OptionType.__members__:
        raise ValueError(f"Invalid option type '{option_type_str}' in full_symbol: {full_symbol}. Expected 'C' or 'P'.")

    # Convert the option type to an OptionType Enum
    option_type = OptionType[option_type_str]

    # Convert the strike price to a float
    try:
        strike_price = float(strike_price_str)
    except ValueError:
        raise ValueError(
            f"Invalid strike price '{strike_price_str}' in full_symbol: {full_symbol}. Expected a numeric value.")

    return symbol, option_type, strike_price




YEAR_TRADING_DAY=244
#预定义到期时间组
HOLIDAYS = [
    '2025-01-01',  # 元旦
    '2025-01-28', '2025-01-29', '2025-01-30', '2025-01-31',
    '2025-02-01', '2025-02-02', '2025-02-03', '2025-02-04',  # 春节
    '2025-04-04', '2025-04-05', '2025-04-06',  # 清明节
    '2025-05-01', '2025-05-02', '2025-05-03', '2025-05-04', '2025-05-05',  # 劳动节
    '2025-05-31', '2025-06-01', '2025-06-02',  # 端午节
    '2025-10-01', '2025-10-02', '2025-10-03', '2025-10-04',
    '2025-10-05', '2025-10-06', '2025-10-07', '2025-10-08'  # 国庆节和中秋节
]


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

def count_remaining_year(expired_date):
    end_date = datetime.datetime.strptime(expired_date, "%Y%m%d").date()
    day_count = count_trading_days(datetime.datetime.now().date(), end_date, HOLIDAYS)
    remaining_year = max(round((day_count - 1) / YEAR_TRADING_DAY + inter_daytime(YEAR_TRADING_DAY), 4), 1 / YEAR_TRADING_DAY)
    return remaining_year


def inter_daytime(total_trading_days: int) -> float:
    # Base calculation
    unit_year_daytime = 0.8 / total_trading_days
    now = datetime.datetime.now()

    # Stock market hours
    stock_time_am_open = datetime.datetime(now.year, now.month, now.day, 9, 30)
    # stocktime_amclose = datetime.datetime(now.year, now.month, now.day, 11, 30)
    # stocktime_pmopen = datetime.datetime(now.year, now.month, now.day, 13, 0)
    # stocktime_pmclose = datetime.datetime(now.year, now.month, now.day, 15, 0)

    # Time difference in minutes from the open
    delta_time = (now - stock_time_am_open).total_seconds() / 60

    if delta_time < 0:
        # Before market opens
        unit_year_daytime = 0.8 / total_trading_days
    elif 0 <= delta_time < 120:
        # Morning session
        unit_year_daytime = ((120 - delta_time) / 240 + 0.5) * 0.8 / total_trading_days
    elif 120 <= delta_time < 210:
        # Lunch break
        unit_year_daytime = 0.4 / total_trading_days
    elif 210 <= delta_time < 330:
        # Afternoon session
        unit_year_daytime = (330 - delta_time) / 240 * 0.8 / total_trading_days
    else:
        # After market closes
        unit_year_daytime = 0

    return unit_year_daytime

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
    # print(f"{inter_daytime(YEAR_TRADING_DAY)}")
    # print(validate_option_id("HO2412-C-3800"))
    # print(f'HO2412-C-3800:{filter_index_option("HO2412-C-3800")}')
    # print(get_cash_multiplier('HO20250919'))
    print(count_trading_days(datetime.datetime.now(), datetime.datetime.now(), []))