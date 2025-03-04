import os
import logging
from datetime import datetime

# 确保 logs 文件夹存在
if not os.path.exists('logs'):
    os.makedirs('logs')

class Logger:
    def __init__(self, name):
        # 创建一个 logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:  # 确保只添加一次 handler
            # 获取当前日期
            current_date = datetime.now().strftime('%Y-%m-%d')
            log_file_name = f'logs/{current_date}.log'

            # 创建文件处理器
            file_handler = logging.FileHandler(log_file_name, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)

            # 创建格式化器并将其添加到处理器
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # 添加处理器到 logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)



