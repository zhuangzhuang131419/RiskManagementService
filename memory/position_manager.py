from model.direction import Direction
from typing import Dict

from model.position import Position


class PositionManager:
    def __init__(self):

        self.symbol_position_dict: Dict[str, ]
        self.position_dict: Dict[str, Position] = {}