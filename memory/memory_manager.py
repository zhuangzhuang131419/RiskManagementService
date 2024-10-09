from helper.Helper import is_index_future, is_index_option
from memory.future_manager import FutureManager
from memory.option_manager import OptionManager
from model.instrument.instrument import Future, Option


class MemoryManager:
    option_manager = None
    future_manager = None

    def __init__(self, instrument_ids: [str]):
        self.init_future_option(instrument_ids)


    def init_future_option(self, instrument_ids: [str]):
        index_options = []
        index_futures = []
        for instrument_id in instrument_ids:
            if is_index_option(instrument_id):
                index_options.append(Option(instrument_id))
            elif is_index_future(instrument_id):
                index_futures.append(Future(instrument_id))

        self.future_manager = FutureManager(index_futures)
        self.option_manager = OptionManager(index_options)

