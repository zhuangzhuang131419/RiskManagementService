import re
from abc import abstractmethod

from typing import Dict

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
    strike_price: float
    symbol: str

    def __init__(self, instrument_id: str, expired_date: str, exchange_id: str):
        super().__init__(instrument_id, expired_date, exchange_id)
        self.greeks = Greeks()

    def is_call_option(self):
        """判断是否为看涨期权"""
        return self.option_type == 'C'

    def is_put_option(self):
        """判断是否为看跌期权"""
        return self.option_type == 'P'


class ETFOption(Option):
    def __init__(self, instrument_id: str, expired_date: str, option_type: str, strike_price: str, exchange_id: str, underlying_instr_id: str):
        super().__init__(instrument_id, expired_date, exchange_id)
        self.option_type = option_type
        self.strike_price = float(strike_price)
        self.symbol = underlying_instr_id + expired_date
        self.full_symbol = self.symbol + "-" + self.option_type + "-" + str(strike_price)

    def __str__(self):
        """返回期权的详细信息"""
        return (f"期权标的物: {self.symbol}\n"
                f"到期日期: {self.expired_date}\n"
                f"期权类型: {self.option_type}\n"
                f"行权价: {self.strike_price}")

class IndexOption(Option):
    def __init__(self, instrument_id: str, expired_date: str, exchange_id: str):
        # eg. io2410-C-4100
        super().__init__(instrument_id, expired_date, exchange_id)
        if validate_option_id(instrument_id):
            self.option_type = instrument_id[7]
            self.strike_price = float(instrument_id.split('-')[-1])
            self.symbol = instrument_id[:2] + expired_date
            self.full_symbol = self.symbol + "-" + self.option_type + "-" + str(self.strike_price)
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

    def set_position(self, option_type: OptionType, position, long: bool):
        if option_type == OptionType.C:
            if long:
                self.call.position.long = position
            else:
                self.call.position.short = position

        if option_type == OptionType.P:
            if long:
                self.put.position.long = position
            else:
                self.put.position.short = position


    def get_position(self, option_type: OptionType):
        if option_type == OptionType.C:
            return self.call.position

        if option_type == OptionType.P:
            return self.put.position

        print(f"Invalid {option_type}")
        raise ValueError