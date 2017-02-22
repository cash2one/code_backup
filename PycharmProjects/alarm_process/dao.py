#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Dao:
    def __init__(self):
        self.engine = create_engine('mysql://oc:oc@10.101.1.141:3306/oc', echo=False)
        self.db_session = sessionmaker(bind=self.engine)


if __name__ == '__main__':
    pass