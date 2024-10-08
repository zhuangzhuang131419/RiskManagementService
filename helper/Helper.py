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

def is_index_future(instrument_id: str) -> bool:
    """
    :param instrument_id: 合约id
    :return: 是否是指数期货
    """
    return any(instrument_id.startswith(future_prefix) for future_prefix in INDEX_FUTURE_PREFIXES)

# 判断合约是不是在option
def is_index_option(instrument_id: str) -> bool:
    """
    :param instrument_id: 合约id
    :return: 是否是指数期权
    """
    return any(instrument_id.startswith(option_prefix) for option_prefix in INDEX_OPTION_PREFIXES)