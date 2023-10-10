#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.singleton import singleton

from core.config import config

@singleton
class MessageService(object): 
    """MessageService
    a service to handle global message
    """

    def __init__(self):
        self.messages = []

    def push(self, msg = None):
        if len(self.messages) >= 5:
            self.messages = self.messages[1:5]
        self.messages.append(msg)

    def get(self):
        return self.messages
