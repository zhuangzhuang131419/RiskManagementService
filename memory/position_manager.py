from model.direction import Direction
from typing import Dict


class PositionManager:
    def __init__(self):
        #
        self.position_details = {}
        self.position: Dict[str, int] = {}

    def update_position(self, exchange_id: str, instrument_id: str, direction: int, volume: int, open_price: float, open_date: str):
        if instrument_id not in self.position:
            self.position[instrument_id] = 0

        if direction == 0:
            self.position[instrument_id] -= volume
        elif direction == 1:
            self.position[instrument_id] += volume

    def update_position_detail(self, exchange_id: str, instrument_id: str, direction: int, volume: int, open_price: float, open_date: str):
        pass