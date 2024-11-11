class Test:
    t = 1

class A:
    def __init__(self, test: Test):
        self.t = test


if __name__ == '__main__':
    t = Test()
    a = A(t)
    t.t = 2
    print(a.t.t)