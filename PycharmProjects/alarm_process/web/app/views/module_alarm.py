#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'kun'
from flask import render_template, request
from latency_monitor_v3 import thirdysix_to_ten
from web.app import app
from web.app.daos import mysql_dao


@app.route('/')
@app.route('/index')
def index():
    flag = True
    param = request.query_string
    if not param:
        return 'url错误'
    if len(param) > 6:
        flag = False
    else:
        for x in param:
            if not str.isalnum(x):
                flag = False
                break
    if flag:
        sms_id = thirdysix_to_ten(param)
        mysql_dao_obj = mysql_dao.MysqlDao()
        all_node = mysql_dao_obj.get_module_alarm_by_smsid(sms_id)
        return render_template('module_alarm.html', all_node=all_node)
    else:
        return '参数错误,未找到数据'

