from queue import Queue

from flask import Flask, jsonify, Blueprint
from helper.helper import filter_index_future, filter_index_option, filter_etf
from memory.future_manager import FutureManager
from memory.option_manager import OptionManager
from model.instrument.instrument import Future
from model.instrument.option import Option


class MemoryManager:
    cffex_option_manager = None
    future_manager = None
    se_option_manager = None



    def __init__(self):

        # self.init_future_option(instruments)
        self.market_data = Queue()
        self.future_manager = None
        self.cffex_option_manager = None
        self.se_option_manager = None


    def init_cffex_instrument(self, instruments: dict):
        index_options = []
        index_futures = []
        for instrument_id, instrument in instruments.items():
            if filter_index_option(instrument_id):
                index_options.append(instrument)
            elif filter_index_future(instrument_id):
                index_futures.append(instrument)
        if len(index_futures) > 0:
            self.future_manager = FutureManager(index_futures)
        if len(index_options) > 0:
            self.cffex_option_manager = OptionManager(index_options)


    def init_se_instrument(self, instruments: dict):
        etf_options = []
        for instrument_id, instrument in instruments.items():
            etf_options.append(instrument)

        if len(etf_options) > 0:
            self.se_option_manager = OptionManager(etf_options)


