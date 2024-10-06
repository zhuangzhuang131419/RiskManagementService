import time

import numpy as np
from CTPManager import CTPManager

def main():
    # 初始化
    ctp_manager = CTPManager()
    ctp_manager.connect_to_market_data()
    time.sleep(3)
    ctp_manager.connect_to_trader()
    time.sleep(3)
    ctp_manager.query_instrument()

    while True:
        print("Heartbreak...")
        time.sleep(10)

if __name__ == "__main__":
    main()