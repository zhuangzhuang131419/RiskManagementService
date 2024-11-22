class Position:
    """Class to hold long and short position information for a single instrument."""

    def __init__(self, instrument_id: str):
        self.instrument_id = instrument_id
        self.long = 0  # 多头仓位数量
        self.short = 0  # 空头仓位数量
        self.open_volume = 0 # 开仓总数

    def __str__(self):
        return (
            f"Instrument ID: {self.instrument_id}, Long: {self.long}, Short: {self.short}, Open Volume: {self.open_volume}"
        )

