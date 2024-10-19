from flask import Flask, jsonify, Blueprint
from helper.helper import is_index_future, is_index_option
from memory.future_manager import FutureManager
from memory.option_manager import OptionManager
from model.instrument.instrument import Future
from model.instrument.option import Option


class MemoryManager:
    option_manager = None
    future_manager = None

    def __init__(self, instruments: dict):
        self.init_future_option(instruments)


    def init_future_option(self, instruments: dict):
        index_options = []
        index_futures = []
        for instrument_id, expired_date in instruments.items():
            if is_index_option(instrument_id):
                index_options.append(Option(instrument_id, expired_date))
            elif is_index_future(instrument_id):
                index_futures.append(Future(instrument_id, expired_date))

        self.future_manager = FutureManager(index_futures)
        self.option_manager = OptionManager(index_options)

