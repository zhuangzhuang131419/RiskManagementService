import re
from abc import abstractmethod

from typing import Dict, TypeVar, Generic

from model.enum.category import Category, UNDERLYING_CATEGORY_MAPPING
from model.enum.option_type import OptionType
from model.instrument.instrument import Instrument
from model.memory.greeks import Greeks
from model.memory.imply_price import ImplyPrice
from model.memory.t_imply_volatility import TImplyVolatility
from model.position import Position


def validate_option_id(instrument_id):
    pattern = r'^[A-Z]{2}\d{4}-[CP]-\d+$'
    if not re.match(pattern, instrument_id, re.IGNORECASE):
        return False
    return True

class Option(Instrument):
    option_type: str
    strike_price: int
    symbol: str

    def __init__(self, instrument_id: str, expired_date: str, exchange_id: str, underlying_multiple: float):
        super().__init__(instrument_id, expired_date, exchange_id)
        self.underlying_multiple = underlying_multiple
        self.greeks = Greeks()

    def is_call_option(self):
        """判断是否为看涨期权"""
        return self.option_type == 'C'

    def is_put_option(self):
        """判断是否为看跌期权"""
        return self.option_type == 'P'


class ETFOption(Option):
    def __init__(self, instrument_id: str, expired_date: str, option_type: str, strike_price: int, exchange_id: str, underlying_instr_id: str, underlying_multiple: float):
        super().__init__(instrument_id, expired_date, exchange_id, underlying_multiple)
        self.option_type = option_type
        self.strike_price = strike_price
        self.symbol = underlying_instr_id + expired_date
        self.full_symbol = self.symbol + "-" + self.option_type + "-" + str(strike_price)
        if underlying_instr_id in UNDERLYING_CATEGORY_MAPPING:
            self.category = UNDERLYING_CATEGORY_MAPPING[underlying_instr_id]

    def __str__(self):
        """返回期权的详细信息"""
        return (f"期权标的物: {self.symbol}\n"
                f"到期日期: {self.expired_date}\n"
                f"期权类型: {self.option_type}\n"
                f"行权价: {self.strike_price}")

class IndexOption(Option):
    def __init__(self, instrument_id: str, expired_date: str, exchange_id: str, underlying_multiple: float):
        # eg. io2410-C-4100
        super().__init__(instrument_id, expired_date, exchange_id, underlying_multiple)
        if validate_option_id(instrument_id):
            self.option_type = instrument_id[7]
            self.strike_price = int(instrument_id.split('-')[-1])
            self.symbol = instrument_id[:2] + expired_date
            self.full_symbol = self.symbol + "-" + self.option_type + "-" + str(self.strike_price)
            self.category = UNDERLYING_CATEGORY_MAPPING[instrument_id[:2]]
        else:
            raise ValueError(f'期权{instrument_id}不符合')



    def __str__(self):
        """返回期权的详细信息"""
        return (f"期权标的物: {self.symbol}\n"
                f"到期日期: {self.expired_date}\n"
                f"期权类型: {self.option_type}\n"
                f"行权价: {self.strike_price}")


class OptionTuple:
    call: Option = None
    put: Option = None

    def __init__(self):
        self.imply_volatility = TImplyVolatility()

    def set_call(self, call: Option):
        self.call: Option = call

    def set_put(self, put: Option):
        self.put: Option = put

    def set_option(self, option: Option):
        if option.is_call_option():
            self.call = option

        if option.is_put_option():
            self.put = option


    def get_option(self, option_type: OptionType):
        if option_type == OptionType.C:
            return self.call

        if option_type == OptionType.P:
            return self.put

        print(f"Invalid {option_type}")
        raise ValueError

    def __str__(self):
        return f"Call: {self.call.full_symbol}, Put: {self.put.full_symbol}"

