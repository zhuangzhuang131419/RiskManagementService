from model.instrument import Future, Option


class MemoryManager:
    # 指数期货的品种列表
    Index_Future_ProductID = ['IH', 'IF', 'IM']
    # 指数期权的品种列表
    Index_Option_ProductID = ['HO', 'IO', 'MO']

    # 期货合约
    futures = []
    # 期权合约
    options = []

    # 期货月份列表
    # 3*4 3个品种 每个品种4个月份
    # eg. [IH2410,IH2411,IH2412,IH2503,IF2410,IF2411,IF2412,IF2503,IM2410,IM2411,IM2412,IM2503]
    Index_Future_Month_ID = []

    # 期货行情结构
    # 2*6 time, bid,bidv,ask,askv,avail 代表：字段时间，买1价格，买1量，卖1价格，卖1量，是否可交易标记
    Index_Future_Price_Data = []

    # 期权品种月份
    # 3*6 3个品种 每个品种6个月份
    Index_Option_Month_Forward_ID = []
    # 期权品种月份行权价个数
    Index_Option_Month_Strike_Num = []

    # 期权行情结构
    # 四维的numpy
    Option_Price_Data = []


    def __init__(self, instrument_ids):
        self.instrument_ids = instrument_ids
        self.sort_instrument_ids()

    # 判断合约是不是在future
    def is_future(self, instrument_id):
        return any(instrument_id.startswith(future_id) for future_id in self.Index_Future_ProductID)

    # 判断合约是不是在option
    def is_option(self, instrument_id: str):
        return any(instrument_id.startswith(option_id) for option_id in self.Index_Option_ProductID)


    def sort_instrument_ids(self):
        # 对合约种类进行分类
        for instrument_id in self.instrument_ids:
            if self.is_future(instrument_id):
                self.futures.append(Future(instrument_id))
            elif self.is_option(instrument_id):
                self.options.append(Option(instrument_id))