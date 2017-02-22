#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'kun'

from app.views.recipients import blueprint_recipient
from flask import Flask
from flask_bootstrap import Bootstrap
import sys

reload(sys)
sys.setdefaultencoding('utf8')  # 支持中文
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SCRF_ENABLED'] = True

app.register_blueprint(blueprint_recipient)


bootstrap = Bootstrap(app)

from app.views import recipients





