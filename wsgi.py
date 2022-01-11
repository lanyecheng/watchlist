#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# @Time    : 2022/1/11 11:11 AM
# @Author  : maoyingfei
# @File    : wsgi.py

import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from watchlist import app
