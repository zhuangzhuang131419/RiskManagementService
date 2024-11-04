class Position:
    """Class to hold long and short position information for a single instrument."""

    def __init__(self, instrument_id: str):
        self.instrument_id = instrument_id
        self.long_quantity = 0  # 多头仓位数量
        self.short_quantity = 0  # 空头仓位数量

