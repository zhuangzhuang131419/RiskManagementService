from dataclasses import dataclass, field


@dataclass
class TImplyVolatility:
    """
    该结构储存了9维度波动率信息的相关元素。
    """
    # 行权价
    strike_price: float = field(default=0.0)  # 整数形式的行权价

    # C（看涨期权）和 P（看跌期权）分别 买卖波动率
    c_ask_vol: float = field(default=0.0)  # C_Ask_vol，浮动卖价波动率（看涨）
    c_bid_vol: float = field(default=0.0)  # C_Bid_vol，浮动买价波动率（看涨）
    p_ask_vol: float = field(default=0.0)  # P_Ask_vol，浮动卖价波动率（看跌）
    p_bid_vol: float = field(default=0.0)  # P_Bid_vol，浮动买价波动率（看跌）

    # 样本有效性状态: 1为有效，0为初始值，-1为无效
    sample_valid: int = field(default=0)

    x_distance: float = field(default=0.0)

    # 采样波动率和隐含vega值
    # 事先采样的4个行权价
    sample_volatility: float = field(default=0.0)
    imply_vega: float = field(default=0.0)  # 隐含vega值


