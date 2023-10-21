#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from utils.singleton import singleton

@singleton
class LoggerService(object): 
    """LoggerService
    All logging config in a singleton class call at startup
    """

    def startup(self):
        logging.basicConfig(format='%(asctime)s %(levelname)-8.8s %(filename)-20.20s %(lineno)-10.10s %(funcName)-20.20s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
