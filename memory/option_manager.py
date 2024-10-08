from model.instrument import Future, Option

class OptionManager:
    # 期权
    options = list()

    # 期权行权价
    option_month_strike_id = []

    def __init__(self):
        pass

    def add_option(self, option: Option):
        self.options.append(option)