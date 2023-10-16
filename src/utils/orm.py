#!/usr/bin/env python3
"""Orm class.
"""

from models.graph import GraphService, db, Graph, Node, Edge

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
        db.drop_tables([Graph, Node, Edge])
        db.create_tables([Graph, Node, Edge])
        
        GraphService().loadGexf('misc/sample.xml')

