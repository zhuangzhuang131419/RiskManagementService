from datetime import time
from dataclasses import dataclass, field

@dataclass
class MarketData:
    bid_price: float = 0.0
    ask_price: float = 0.0
    bid_volume: int = 0
    ask_volume: int = 0
    available: int = 0
    time: time = None