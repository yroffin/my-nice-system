#!/usr/bin/env python3
"""Orm class.
"""

from models.graph import GraphService, Style, db, Graph, Node, Edge

from nicegui import app

from utils.singleton import singleton

from typing import Optional
from core.config import config
import logging

@singleton
class OrmService(object): 
    """OrmService
   handle all orm setup
    """

    def __init__(self):
        None

    def startup(self):
        logging.info('Load ORM')
        db.connect()
        if False:
            db.drop_tables([Graph, Node, Edge, Style])
            db.create_tables([Graph, Node, Edge, Style])

