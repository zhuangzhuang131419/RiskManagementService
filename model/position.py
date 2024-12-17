class Position:
    """Class to hold long and short position information for a single instrument."""

    def __init__(self, instrument_id: str):
        self.instrument_id = instrument_id
        self.long = 0  # 多头仓位数量
        self.short = 0  # 空头仓位数量
        self.long_open_volume = 0 # 多头开仓总数
        self.short_open_volume = 0 # 空头开仓总数
        self.long_close_volume = 0 # 多头平仓总数
        self.short_close_volume = 0  # 空头平仓总数

    def __str__(self):
        return (
            f"Instrument ID: {self.instrument_id}, Long: {self.long}, Short: {self.short}, 买开: {self.long_open_volume}, 卖开：{self.short_open_volume}, 买平：{self.long_close_volume} 卖平：{self.short_close_volume}"
        )

    def __add__(self, other):
        """Add two Position objects together."""
        if not isinstance(other, Position):
            raise TypeError("Both objects must be of type Position")

        combined = Position(self.instrument_id)
        combined.long = self.long + other.long
        combined.short = self.short + other.short
        combined.long_open_volume = self.long_open_volume + other.long_open_volume
        combined.short_open_volume = self.short_open_volume + other.short_open_volume
        combined.long_close_volume = self.long_close_volume + other.long_close_volume
        combined.short_close_volume = self.short_close_volume + other.short_close_volume
        return combined

