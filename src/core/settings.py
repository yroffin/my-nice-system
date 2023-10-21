#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Env Config
    ENVIRONMENT: str = ''

    # default yaml config file    
    CONFIG_YAML_LOCATION: str = ".tmp/.config.yaml"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
