__author__ = 'Harutya'
__date__ = '2021/7/52021/07/05'

import logging
import os


class Logger:
    def __init__(self):
        # 创建一个logger
        self.logger = logging.getLogger(name="harutya-lol-api")
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于将日志输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')

        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(ch)

    def get_log(self):
        """定义一个函数，回调logger实例"""
        return self.logger
