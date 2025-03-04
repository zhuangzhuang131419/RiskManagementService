import numpy as np
from dataclasses import dataclass, field


@dataclass
class ATMPram:
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

    def __str__(self) -> str:
        # 格式化 volatility_points 数组
        volatility_points_str = ", ".join(f"{v:.2f}" for v in self.volatility_points)

        return (
            f"ATMVolatility(\n"
            f"  atm_valid={self.atm_valid},\n"
            f"  k1_volatility={self.k1_volatility:.2f}, k2_volatility={self.k2_volatility:.2f},\n"
            f"  k3_volatility={self.k3_volatility:.2f}, k4_volatility={self.k4_volatility:.2f},\n"
            f"  atm_volatility_protected={self.atm_volatility_protected:.2f},\n"
            f"  atm_gamma={self.atm_gamma:.2f}, atm_vega={self.atm_vega:.2f},\n"
            f"  volatility_points=[{volatility_points_str}]\n"
            f")"
        )

