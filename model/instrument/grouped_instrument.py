
from dataclasses import dataclass
from typing import Union, Optional

from model.instrument.future import Future
from model.instrument.option import OptionTuple
from model.instrument.option_series import OptionSeries
from model.memory.wing_model_para import WingModelPara


@dataclass
class GroupedInstrument:
    def __init__(self, future = None, index_option_series = None, etf_option_series = None):
        self.future: Optional[Future]= future
        self.index_option_series: Optional[OptionSeries] = index_option_series
        self.etf_option_series: Optional[OptionSeries] = etf_option_series
        self.customized_wing_model_para = WingModelPara()

    def __str__(self):
        return f"GroupedInstrument(Future: {self.future},Index Option Series: {self.index_option_series},ETF Option Series: {self.etf_option_series}"