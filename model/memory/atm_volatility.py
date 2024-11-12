import numpy as np
from dataclasses import dataclass, field


@dataclass
class ATMVolatility:
    """
    该结构储存了计算中心波动率过程中的重要信息与最终结果。
    """
    # 当前ATM有效性
    atm_valid: bool = field(default=False)

    # 各个行权价对应的波动率
    k1_volatility: float = field(default=-1)
    k2_volatility: float = field(default=-1)
    k3_volatility: float = field(default=-1)
    k4_volatility: float = field(default=-1)

    # 序列保护的ATM波动率
    atm_volatility_protected: float = field(default=-1)

    # ATM相关的希腊字母
    atm_gamma: float = field(default=-1)  # Gamma
    atm_vega: float = field(default=-1)  # Vega

    # 波动率计算中的点位（如X-1.98, X-1.32等），用于不同价格附近的波动率估计
    # 依次代表-1.98, -1.32, -0.66, 0, 0.66, 1.32, 1.98的点位
    volatility_points: np.ndarray = field(default_factory=lambda: np.full(7, -1.0, dtype=float))

