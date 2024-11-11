class UserMemoryManager:
    def __init__(self):
        self.order_ref = 0

    def get_order_ref(self):
        order_ref = str(self.order_ref).zfill(12)
        self.order_ref += 1
        return order_ref