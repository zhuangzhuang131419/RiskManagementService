from typing import Generic, TypeVar

T = TypeVar('T')


class Test:
    t = 1

class A(Generic[T]):
    def __init__(self, test: T):
        self.t = test


if __name__ == '__main__':
    a = A(Test)
    print(a.t.t)