
from dataclasses import dataclass
from typing import Union

from model.instrument.future import Future
from model.instrument.option import OptionTuple
from model.instrument.option_series import OptionSeries
from model.memory.wing_model_para import WingModelPara


@dataclass
class GroupedInstrument:
    future: Union[Future, None]
    index_option_series: Union[OptionSeries, None]
    etf_option_series: Union[OptionSeries, None]
    customized_wing_model_para: WingModelPara = WingModelPara()

    def __str__(self):
        return f"GroupedInstrument(Future: {self.future},Index Option Series: {self.index_option_series},ETF Option Series: {self.etf_option_series}"