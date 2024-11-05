from enum import Enum

class OptionType(Enum):
    C = 0  # Call
    P = 1  # Put

# 将整数转换为 OptionType
def to_option_type(value: int) -> OptionType:
    try:
        return OptionType(value)
    except ValueError:
        raise ValueError(f"Invalid integer for OptionType: {value}")

if __name__ == '__main__':
    print(OptionType("C"))