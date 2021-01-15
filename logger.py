#-*-coding:utf-8-*-
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import multiprocessing as mp

def get_logger(proc_name="log_DpEngine"):
    # create log file
    log_file = './log/' + proc_name + '.log'
    if not os.path.exists('./log'):
        os.mkdir('./log')
    if not os.path.exists(log_file):
        open(log_file, "a+").close()
    # logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)# logging.DEBUG
    # fhandler
    handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=30)
    strfmt = "[%(asctime)s] %(filename)s[line:%(lineno)d] %(levelname)s %(message)s"
    # format
    formatter = logging.Formatter(strfmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    std_handler = logging.StreamHandler(sys.stdout)
    std_handler.setFormatter(formatter)
    logger.addHandler(std_handler)
    return logger
logger = get_logger()
