from dataclasses import dataclass
from typing import Dict

from model.enum.category import Category


@dataclass
class GreeksTotalResp:
    user: str
    greeks_total_by_category : Dict[Category, Dict[str, float]]

    def __init__(self, user_name: str):
        self.user = user_name
        self.greeks_total_by_category = {}

    def to_dict(self):
        """
        Converts the instance of GreeksTotalResp to a dictionary.
        """

        result = { "user": self.user }
        for category, greeks in self.greeks_total_by_category.items():
            result[category.value] = {k: v for k, v in greeks.items()}

        return result

