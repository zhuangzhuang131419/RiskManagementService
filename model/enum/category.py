from enum import Enum
from typing import Dict, Tuple, List

class Category(Enum):
    SSE50 = "SSE50"
    CSI300 = "CSI300"
    CSI500 = "CSI500"

INDEX_OPTION_ETF_OPTION_FUTURE_MAPPING = {
    Category.SSE50: {"HO", "510050", "IH"},
    Category.CSI300: {"IO", "510300", "IF"},
    Category.CSI500: {"MO", "510500", "IM"}
}

UNDERLYING_CATEGORY_MAPPING: Dict[str, Category] = {
    "HO": Category.SSE50,
    "510050": Category.SSE50,
    "IH": Category.SSE50,
    "IO": Category.CSI300,
    "510300": Category.CSI300,
    "IF": Category.CSI300,
    "MO": Category.CSI500,
    "510500": Category.CSI500,
    "IM": Category.CSI500
}