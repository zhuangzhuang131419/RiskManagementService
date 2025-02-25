from typing import Dict, List

from utils.helper import filter_index_future, filter_etf_option, filter_index_option
from model.config.exchange_config import ExchangeConfig
from model.enum.exchange_type import ExchangeType
from model.position import Position


class UserMemoryManager:
    def __init__(self, user_name: str, exchange_configs: Dict[ExchangeType, List[ExchangeConfig]]):
        self.order_ref = 0
        self.exchange_configs = exchange_configs
        # investor_id -> future_id -> position
        self.positions: Dict[str, Dict[str, Position]] = {}
        self.refresh_position()
        self.user = user_name


    def get_order_ref(self):
        order_ref = str(self.order_ref).zfill(12)
        self.order_ref += 1
        return order_ref

    def refresh_position(self):
        self.positions: Dict[str, Dict[str, Position]] = {}
        for exchange_type, exchange_config in self.exchange_configs.items():
            for config in exchange_config:
                self.positions[config.investor_id] = {}

    def get_combined_position(self):
        """Combine positions for each full_symbol."""
        combined_positions = {}
        for investor_id, positions in self.positions.items():
            for full_symbol, position in positions.items():
                if full_symbol not in combined_positions:
                    combined_positions[full_symbol] = position
                else:
                    combined_positions[full_symbol] += position
        return combined_positions

    def print_position(self) -> str:
        if not self.positions:
            return "No positions available."

        result = []
        for investor_id, futures in self.positions.items():
            for future_id, position in futures.items():
                result.append(f"{investor_id} ({future_id}): {position}")

        return "\n".join(result)




