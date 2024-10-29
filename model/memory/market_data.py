from datetime import time
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class MarketData:
    bid_prices: List[float] = field(default_factory=lambda: [-1.0] * 5)
    ask_prices: List[float] = field(default_factory=lambda: [-1.0] * 5)
    bid_volumes: List[int] = field(default_factory=lambda: [-1] * 5)
    ask_volumes: List[int] = field(default_factory=lambda: [-1] * 5)
    available: int = 0
    time: time = None

    def set_available(self):
        self.available = 1 if self.ask_volumes[0] > 0 and self.bid_volumes[0] > 0 and self.ask_prices[0] > 0 and self.bid_prices[0] > 0 else 0

@dataclass
class DepthMarketData(MarketData):
    instrument_id: str = ""
    exchange_id: str = ""

    def clean_data(self):
        threshold = 1.7976931348623157e+308
        tolerance = 0.000001

        self.bid_prices = [-1 if abs(data - threshold) < tolerance else data for data in self.bid_prices]
        self.ask_prices = [-1 if abs(data - threshold) < tolerance else data for data in self.ask_prices]
        self.bid_volumes = [-1 if abs(data - threshold) < tolerance else data for data in self.bid_volumes]
        self.ask_volumes = [-1 if abs(data - threshold) < tolerance else data for data in self.ask_volumes]

