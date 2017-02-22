#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'kun'
import MySQLdb
import MySQLdb.cursors

from logger import log


def get_thredholds(conn):
    retval = {}
    try:
        sql = "SELECT * FROM latency_monitor_threshold"
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        retval = cursor.fetchall()
        cursor.close()
    except MySQLdb.Error, e:
        log.error('get threshold db error:%d: %s' % (e.args[0], e.args[1]))
    print 'threholds'
    print retval


def get_recipient(conn):
    retval = {}
    res = {}
    try:
        sql = "SELECT module,phone,email,sms_max FROM latency_monitor_recipient"
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
    except MySQLdb.Error, e:
        log.error('get recipients db error:%d: %s' % (e.args[0], e.args[1]))
    for x in res:
        if not x['phone']:
            x['phone'] = ""
        if not x['email']:
            x['email'] = ""
        # 将字典形式保存的phone信息和email转换为list
        x['phone'] = [p.strip() for p in x['phone'].split(',')]
        x['email'] = [p.strip() for p in x['email'].split(',')]
        retval[x['module']] = x
    print 'recipients'
    print retval

if __name__ == '__main__':
    log.info("begain to get thredholds info")
    conn = MySQLdb.connect(
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            host="10.101.1.141",
            user="oc",
            passwd="oc",
            port=3306,
            db="oc"
    )

    get_thredholds(conn)
    get_recipient(conn)