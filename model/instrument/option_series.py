from model.instrument.option import Option


class OptionSeries:
    def __init__(self, name: str, options: [Option]):
        """
        初始化期权系列。

        :param name: 期权的名字，例如 'HO2410' 表示某个品种（HO）和月份（2410）的期权系列。
        :param options: 期权对象列表，包含该系列的所有期权。
        """
        self.name = name # 期权名字，例如 'HO2410'
        self.options = {}

        for option in options:
            self.options[option.strike_price] = option

    def get_option(self, strike_price):
        return self.options.get(strike_price)

    def get_all_strike_price(self):
        return sorted(self.options.keys())
