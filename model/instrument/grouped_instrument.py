
from dataclasses import dataclass
from typing import Union

from model.instrument.future import Future
from model.instrument.option import OptionTuple
from model.instrument.option_series import OptionSeries


@dataclass
class GroupedInstrument:
    future: Union[Future, None]
    index_option_series: Union[OptionSeries, None]
    etf_option_series: Union[OptionSeries, None]

    def __str__(self):
        return f"GroupedInstrument(Future: {self.future},Index Option Series: {self.index_option_series},ETF Option Series: {self.etf_option_series}"