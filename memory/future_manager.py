from model.instrument import Future


class FutureManager:
    # 期货合约
    futures = list()

    def __init__(self):
        pass

    def add_future(self, future: Future):
        self.futures.append(future)
