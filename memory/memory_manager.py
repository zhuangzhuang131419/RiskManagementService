from memory.future_manager import FutureManager
from memory.option_manager import OptionManager
from model.instrument import Future, Option


class MemoryManager:
    # 指数期货的品种列表
    Index_Future_ProductIDlist = ['IH', 'IF', 'IM']
    # 指数期权的品种列表
    Index_Option_ProductIDlist = ['HO', 'IO', 'MO']

    def __init__(self):
        self.future_manager = FutureManager()
        self.option_manager = OptionManager()

    # 添加一个合约
    def add_instrument(self, instrument_id):
        if self.is_future(instrument_id):
            self.future_manager.add_future(Future(instrument_id))
        elif self.is_option(instrument_id):
            self.option_manager.add_option(Option(instrument_id))

    def add_instruments(self, instrument_ids):
        for instrument_id in instrument_ids:
            self.add_instrument(instrument_id)

    # 判断合约是不是在future
    def is_future(self, instrument_id):
        return any(instrument_id.startswith(future_id) for future_id in self.Index_Future_ProductIDlist)

    # 判断合约是不是在option
    def is_option(self, instrument_id: str):
        return any(instrument_id.startswith(option_id) for option_id in self.Index_Option_ProductIDlist)