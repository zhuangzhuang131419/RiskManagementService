
from dataclasses import dataclass
from typing import Union

from model.instrument.future import Future
from model.instrument.option import OptionTuple

@dataclass
class GroupedInstrument:
    future: Union[Future, None]
    index_option_tuple: Union[OptionTuple, None]
    etf_option_tuple: Union[OptionTuple, None]