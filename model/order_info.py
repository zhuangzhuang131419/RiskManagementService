from dataclasses import dataclass

@dataclass
class OrderInfo(object):
    def __init__(self, order_ref, front_id, session_id):
        self.front_id = front_id  # 前置编号
        self.session_id = session_id  # 会话编号
        self.order_ref = order_ref  # 最大报单引用
        self.pOrder = None
        self.order_price = None
        self.instrument_id = None

    def __str__(self):
        return (f"OrderInfo(\n"
                f"  front_id: {self.front_id},\n"
                f"  session_id: {self.session_id},\n"
                f"  max_order_ref: {self.order_ref},\n"
                f"  order_price: {self.order_price},\n"
                f"  instrument_id: {self.instrument_id},\n"
                f"  pOrder: {self.pOrder}\n"
                f")")