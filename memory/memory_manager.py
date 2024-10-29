from queue import Queue

from typing import Dict
from flask import Flask, jsonify, Blueprint
from helper.helper import filter_index_future, filter_index_option, filter_etf
from memory.future_manager import FutureManager
from memory.option_manager import OptionManager
from model.instrument.instrument import Future
from model.instrument.option import Option


class MemoryManager:
    cffex_option_manager: OptionManager = None
    future_manager: FutureManager = None
    se_option_manager: OptionManager = None

    def __init__(self):

        # self.init_future_option(instruments)
        self.market_data = Queue()

        # 负责把ETF instrument_id 转成可读的 instrument_id
        self.se_instrument: Dict[str, str] = {}


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

        for instrument in instruments.values():
            etf_options.append(instrument)
            self.se_instrument[instrument.id] = instrument.instrument_id

        print(f"se_instrument:{self.se_instrument}")

        if len(etf_options) > 0:
            self.se_option_manager = OptionManager(etf_options)


