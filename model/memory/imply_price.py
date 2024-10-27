from dataclasses import dataclass, field


@dataclass
class ImplyPrice:
    """
    该结构储存了计算隐含价格过程中的重要信息与最终结果。
    """
    # 期货价格有效性状态：1 表示有效，0 表示初始值，-1 表示无效
    future_valid: int = field(default=-1)

    # 远期价格
    forward_ask: float = field(default=-1)  # 远期卖价
    forward_bid: float = field(default=-1)  # 远期买价

    # 最优远期的卖出和买入行权价
    ask_strike: float = field(default=-1)  # 卖出行权价
    bid_strike: float = field(default=-1)  # 买入行权价

    # ATM（平值期权）有效性和价格
    atm_valid: int = field(default=-1)  # 1 表示有效，0 表示初始值，-1 表示无效
    atms_ask: float = field(default=-1)  # 平值卖价
    atms_bid: float = field(default=-1)  # 平值买价

    # 平值期权附近的行权价
    k1: float = field(default=-1)  # 平值左侧第二行权价
    k2: float = field(default=-1)  # 平值左侧行权价
    k3: float = field(default=-1)  # 平值右侧行权价
    k4: float = field(default=-1)  # 平值右侧第二行权价

    # 隐含价格
    imply_s_ask: float = field(default=-1)  # 隐含卖价
    imply_s_bid: float = field(default=-1)  # 隐含买价
