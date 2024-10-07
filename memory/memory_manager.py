from model.instrument import Future, Option


class MemoryManager:
    # 指数期货的品种列表
    Index_Future_ProductIDlist = ['IH', 'IF', 'IM']
    # 指数期权的品种列表
    Index_Option_ProductIDlist = ['HO', 'IO', 'MO']

    # 期货合约
    futures = []

    # 期权合约
    options = []

    # 期权行权价
    option_month_strike_id = []


    def __init__(self, instrument_ids):
        self.instrument_ids = instrument_ids
        self.sort_instrument_ids()

    # 判断合约是不是在future
    def is_future(self, instrument_id):
        return any(instrument_id.startswith(future_id) for future_id in self.Index_Future_ProductIDlist)

    # 判断合约是不是在option
    def is_option(self, instrument_id: str):
        return any(instrument_id.startswith(option_id) for option_id in self.Index_Option_ProductIDlist)


    def sort_instrument_ids(self):
        # 对合约种类进行分类
        for instrument_id in self.instrument_ids:
            if self.is_future(instrument_id):
                self.futures.append(Future(instrument_id))
            elif self.is_option(instrument_id):
                self.options.append(Option(instrument_id))