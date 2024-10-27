from dataclasses import dataclass, field


@dataclass
class Greeks:
    """
    该结构存储了期权的希腊字母（Greeks）及相关的风险敏感度指标。
    """
    # 看涨和看跌期权的 Delta
    delta: float = field(default=0.0)  # cDELTA，看涨期权的Delta

    # 其他希腊字母
    gamma: float = field(default=0.0)  # Gamma，Gamma值
    vega: float = field(default=0.0)  # Vega，Vega值
    theta: float = field(default=0.0)  # cTheta，看涨期权的Theta

    # Vanna 和 Volga（对波动率的敏感性）
    vanna_vs: float = field(default=0.0)  # vannaVS，Vanna对标的价格和波动率的敏感性
    vanna_sv: float = field(default=0.0)  # vannaSV，Vanna的波动率敏感性

    # 其他敏感度参数
    db: float = field(default=0.0)  # db1%，Delta斜率
    vomma: float = field(default=0.0)  # Vomma1%，vega的2阶导数
    dk1: float = field(default=0.0)  # Dk1_1%，行权价1阶敏感度
    dk2: float = field(default=0.0)  # Dk2_1%，行权价2阶敏感度
    charm: float = field(default=0.0)  # Charm，对时间变化的Delta敏感度
