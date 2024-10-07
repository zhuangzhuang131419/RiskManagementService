from dataclasses import dataclass

@dataclass
class OrderInfo(object):
    def __init__(self, order_ref, strategy_id, front_id, session_id):
        self.frontID = front_id  # 前置编号
        self.sessionID = session_id  # 会话编号
        self.maxOrderRef = order_ref  # 最大报单引用
        self.pOrder = None
        self.strategyID = strategy_id
        self.orderPrice = None
        self.instrumentID = None