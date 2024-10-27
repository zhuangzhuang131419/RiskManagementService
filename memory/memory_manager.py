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



    def __init__(self, instruments: dict):

        self.init_future_option(instruments)
        self.market_data = Queue()


    def init_future_option(self, instruments: dict):
        index_options = []
        index_futures = []
        etf_options = []
        for instrument_id, expired_date in instruments.items():
            if filter_index_option(instrument_id):
                index_options.append(Option(instrument_id, expired_date))
            elif filter_index_future(instrument_id):
                index_futures.append(Future(instrument_id, expired_date))
            elif filter_etf(instrument_id):
                etf_options.append(instrument_id)


        self.future_manager = FutureManager(index_futures)
        self.cffex_option_manager = OptionManager(index_options)
        # self.se_option_manager = OptionManager(etf_options)

