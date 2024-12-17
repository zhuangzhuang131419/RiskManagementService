from enum import Enum

class BaselineType(Enum):
    AVERAGE = "平均基准"
    SH = "上交基准"
    INDIVIDUAL = "各自基准"

if __name__ == '__main__':
    base_type : BaselineType = BaselineType["SH"]
    print(base_type)