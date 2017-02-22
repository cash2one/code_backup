#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'kun'

from app.views.receiver import blueprint_receiver
from flask import Flask
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SCRF_ENABLED'] = True

app.register_blueprint(blueprint_receiver)


bootstrap = Bootstrap(app)

from app.views import receiver





