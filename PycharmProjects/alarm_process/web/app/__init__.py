#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'kun'

from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yidianzixunoc'
app.config['SCRF_ENABLED'] = True
bootstrap = Bootstrap(app)

from web.app.views import module_alarm





