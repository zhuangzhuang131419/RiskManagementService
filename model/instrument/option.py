import re

from numba.cuda.libdevice import trunc

from model.instrument.instrument import Instrument


def validate_option_id(instrument_id):
    pattern = r'^[A-Z]{2}\d{4}-[CP]-\d+$'
    if not re.match(pattern, instrument_id, re.IGNORECASE):
        return False
    return True


class Option(Instrument):
    def __init__(self, instrument_id: str, expired_date: str):
        super().__init__(instrument_id, expired_date)
        # eg. io2410-C-4100
        if validate_option_id(instrument_id):
            self.symbol = self.id.split('-')[0]
            self.option_type = self.id[7]
            self.strike_price = self.id.split('-')[-1]
        else:
            raise ValueError(f'期权{instrument_id}不符合')

    def is_call_option(self):
        """判断是否为看涨期权"""
        return self.option_type == 'C'

    def is_put_option(self):
        """判断是否为看跌期权"""
        return self.option_type == 'P'

    def __str__(self):
        """返回期权的详细信息"""
        return (f"期权标的物: {self.symbol}\n"
                f"到期日期: {self.expired_date}\n"
                f"期权类型: {self.option_type}\n"
                f"行权价: {self.strike_price}")

if __name__ == '__main__':
    o = Option("IO2410-C-4100", "")
    o1 = Option("io2410-C-4100", "")