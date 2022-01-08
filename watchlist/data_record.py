#!/usr/bin/env python
# -*- coding: utf-8 -*-

from watchlist import db
from watchlist.models import Records


def insert_record(xmind_name, note=''):
    r1 = Records(title=xmind_name, note=note)
    db.session.add(r1)
    db.session.commit()
