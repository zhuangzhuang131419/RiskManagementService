
from dataclasses import dataclass
from typing import Union

from model.instrument.future import Future
from model.instrument.option import OptionTuple

@dataclass
class GroupedInstrument:
    future: Union[Future, None]
    index_option_tuple: Union[OptionTuple, None]
    etf_option_tuple: Union[OptionTuple, None]

    def __str__(self):
        return (
            f"GroupedInstrument(\n"
            f"  Future: {self.future},\n"
            f"  Index Option Tuple: {self.index_option_tuple},\n"
            f"  ETF Option Tuple: {self.etf_option_tuple}\n"
            f")"
        )