class Instrument:
    id: str

    def __init__(self, instrument_id):
        self.id = instrument_id

class Option(Instrument):
    def __init__(self, instrument_id: str):
        super().__init__(instrument_id)
        # eg. io2410-C-4100
        self.code = self.id[:2]
        self.symbol = self.id.split('-')[0]
        self.expiry_month = self.id[2:6]
        self.option_type = self.id[7]
        self.strike_price = self.id.split('-')[-1]

    def is_call_option(self):
        """判断是否为看涨期权"""
        return self.option_type == 'C'

    def is_put_option(self):
        """判断是否为看跌期权"""
        return self.option_type == 'P'


    def validate_option_code(self):
        """校验期权代码的合法性"""
        if len(self.id) != 13:
            raise ValueError(f"期权代码长度应为13位，当前为 {len(self.id)} 位")

        if not self.id[2:6].isdigit():
            raise ValueError(f"到期日期应为数字（年和月），当前为 {self.id[2:6]}")

        if self.id[7] not in ['C', 'P']:
            raise ValueError(f"期权类型无效，应为 'C'（看涨期权）或 'P'（看跌期权），当前为 {self.id[7]}")

        if not self.id.split('-')[-1].isdigit():
            raise ValueError(f"行权价应为数字，当前为 {self.id.split('-')[-1]}")

    def __str__(self):
        """返回期权的详细信息"""
        return (f"期权标的物: {self.symbol}\n"
                f"到期日期: {self.expiry_month}\n"
                f"期权类型: {self.option_type}\n"
                f"行权价: {self.strike_price}")

class Future(Instrument):

    def __init__(self, instrument_id):
        super().__init__(instrument_id)
        # eg. IH2412
        self.symbol = self.id[:2]
        self.bid = float
        self.ask = float
        self.bid_volume = float
        self.ask_volume = float
        self.available = True