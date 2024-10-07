from enum import Enum

# 定义 Direction 枚举类
class Direction(Enum):
    BUY_OPEN = ('buyopen', '买开仓')
    BUY_CLOSE = ('buyclose', '买平仓')
    SELL_OPEN = ('sellopen', '卖开仓')
    SELL_CLOSE = ('sellclose', '卖平仓')
    BUY_CLOSE_TODAY = ('buyclosetoday', '买平今')
    SELL_CLOSE_TODAY = ('sellclosetoday', '卖平今')
