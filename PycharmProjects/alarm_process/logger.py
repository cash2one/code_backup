#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'kun'


# 日志类
import logging


class Logger:
    def __init__(self, log_name, file_name):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)

        fh = logging.FileHandler(file_name)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -[line:%(lineno)d]%(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def get_logger(self):
        return self.logger

log = Logger('module_alarm', './module_alarm.log').get_logger()

if __name__ == '__main__':
    pass
