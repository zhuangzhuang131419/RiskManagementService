from queue import Queue

from typing import Dict, List
from flask import Flask, jsonify, Blueprint
from helper.helper import filter_index_future, filter_index_option, filter_etf_option
from memory.future_manager import FutureManager
from memory.option_manager import OptionManager
from model.instrument.instrument import Future, Instrument
from model.instrument.option import Option

class MemoryManager:
    def __init__(self):

        # self.init_future_option(instruments)
        self.market_data = Queue()
        self.option_manager = OptionManager()
        self.future_manager = FutureManager()


    def init_cffex_instrument(self, instruments: Dict[str, Instrument]):
        index_options = []
        index_futures = []
        for instrument_id, instrument in instruments.items():
            if filter_index_option(instrument_id):
                index_options.append(instrument)
            elif filter_index_future(instrument_id):
                index_futures.append(instrument)
        if len(index_futures) > 0:
            self.future_manager.add_index_future(index_futures)
        if len(index_options) > 0:
            self.option_manager.add_options(index_options)

    def init_se_instrument(self, instruments: Dict[str, Instrument]):
        etf_options = []

        for instrument in instruments.values():
            expiration_month = instrument.expired_month
            etf_options.append(instrument)

        if len(etf_options) > 0:
            self.option_manager.add_options(etf_options)






