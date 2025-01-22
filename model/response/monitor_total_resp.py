from dataclasses import dataclass
from typing import Dict

from model.enum.category import Category


@dataclass
class MonitorTotalResp:
    user: str
    monitor_total_by_category : Dict[Category, str]

    def __init__(self, user_name: str):
        self.user = user_name
        self.monitor_total_by_category = {}

    def to_dict(self):
        """
        Converts the instance of MonitorTotalResp to a dictionary.
        """

        result = { "user": self.user }
        for category, monitor in self.monitor_total_by_category.items():
            result[category.value] = monitor

        return result

