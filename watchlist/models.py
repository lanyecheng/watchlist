#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from watchlist import db
from datetime import datetime


# 表名将会是 user（自动生成，小写处理）
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(20))  # 名字
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


# 表名将会是 movie
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份


class Records(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    note = db.Column(db.Text)
    create_on = db.Column(db.DateTime, default=datetime.now())
    is_deleted = db.Column(db.Integer, default=0)