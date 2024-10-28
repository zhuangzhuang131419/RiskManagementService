from dataclasses import dataclass, field


@dataclass
class WingModelPara:
    S: float = field(default=0.0)
    k1: float = field(default=0.0)
    k2: float = field(default=0.0)
    b: float = field(default=0.0)
    residual: float = field(default=0.0)