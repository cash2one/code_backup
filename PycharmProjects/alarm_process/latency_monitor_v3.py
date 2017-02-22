#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'kun'
import MySQLdb
import MySQLdb.cursors
import datetime
import time
from send_sms import send_sms
from logger import log

from sqlalchemy import func
from dao import Dao
from table_class import ModuleAlarm


default_error_percentage_threshold = 1  # 1%
default_latency_threshold = 1000  # ms
default_sms_max = 10
default_phones = [u'18611866276', u'18678879533', u'13401161654', u'15801127531', u'13297028626']
default_email = [u'wangfubo@yidian-inc.com', ]


# 保存接收到的报警信息
# 格式:{'module':{'uri':[0,0,0]}}
# key为module和uri,value为一个list,保存最近三分钟该key对应的信息是否达到报警条件
recent_recv_alarm = {}

# 保存接受到的报警时间,保证15分钟内不接收重复报警
# key:'module|uri',value:int  timestamp
# eg:{'module':{'uri1':2233232332,'uri2':11111111}}
last_recv_time = {}

# 保存接受到的报警信息,发短信模块从此字典中取出报警信息发送
# {'module':{'uri':(latency,err_ratio)}}
message = {}

# 10进制和36进制相互转换
# 每一条报警信息对应一个36进制表示的数字,加在短信url链接的尾部,用于唯一标识某一条报警信息
digits = (
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y', 'z'
    )


# 十进制转换位36进制
def ten_to_36(num):
    if num == 0:
        return '0'
    result = []
    while num > 0:
        tmp = num % 36
        num /= 36
        result .append(digits[tmp])
    return ''.join([str(x) for x in result[::-1]])


# 36进制转换为16进制
def thirdysix_to_ten(str_num):
    return int(str_num, 36)


def get_latency(conn):
    """
    # 获取数据库中原始信息
    :param conn:数据库连接
    :return:
    """
    result = {}
    try:
        sql = "SELECT server host,frontend module, uri, SUM(pv) pv, SUM(pv_srv_err) pv_srv_err, SUM(ts)/SUM(pv) latency, \
            start_time recv_time  FROM haproxy_http_m_latency_2 WHERE \
            start_time>(select DATE_SUB(max(start_time), INTERVAL 1 MINUTE) \
            from haproxy_http_m_latency_2) GROUP BY frontend, uri"

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
    except MySQLdb.Error, e:
        log.error('get recipients db error: %d: %s' % (e.args[0], e.args[1]))
    return result


def get_threshold(conn):
    """
    获取报警阈值信息,部分模块和uri有自定义的阈值
    :param conn:数据库连接
    :return:
    """
    retval = {}
    try:
        sql = "SELECT * FROM latency_monitor_threshold"
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        retval = cursor.fetchall()
        cursor.close()
    except MySQLdb.Error, e:
        log.error('get threshold db error:%d: %s' % (e.args[0], e.args[1]))
    return retval


def get_receiver(conn):
    """
    从数据库中取出联系人信息,包括手机号和邮箱.部分模块有默认的通知联系人
    :param conn:数据库连接
    :return:
    """
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
    return retval


def need_recv(canalarm, module, uri):
    """
    # 判断某一条报警信息是否达到报警条件
    :param canalarm:True or False
    :param module:module name
    :param uri:uri
    :return:True or False
    """
    if module not in recent_recv_alarm:
        recent_recv_alarm[module] = {}
    # 没有接收过此信息,说明是第一次达到报警阈值,不认为此信息为报警信息,返回False
    if uri not in recent_recv_alarm[module]:
        recent_recv_alarm[module][uri] = [canalarm]
        log.debug('first receive this alarm:[%s][%s]' % (module, uri))
        return False

    # 更新队列信息
    if len(recent_recv_alarm[module][uri]) == 3:
        log.debug("update queue info:[%s][%s],delete %d,add %d" %
                  (module, uri, recent_recv_alarm[module][uri][0], canalarm))
        del recent_recv_alarm[module][uri][0]

    recent_recv_alarm[module][uri].append(canalarm)

    # 若连续三次达到报警阈值,则判断为报警信息,进行下一步判断
    if len(recent_recv_alarm[module][uri]) == 3 and recent_recv_alarm[module][uri][0] and \
            recent_recv_alarm[module][uri][1] and recent_recv_alarm[module][uri][2]:
        now = int(time.time())
        if module not in last_recv_time:
            last_recv_time[module] = {}
            return True

        # 若15分钟之内没有发送过此报警信息,则需要接收保存,用于下一步发送短信,因此返回True
        if uri not in last_recv_time[module]:
            log.debug("first receive this alarm:[%s][%s]" % (module, uri))
            return True
        # 上次发送此报警信息已经超过15分钟,需要再次接收保存,返回True
        if now - last_recv_time[module][uri] > 15 * 60:
            log.debug("last receive time is 15 minutes ago ,receive it:[%s][%s]" % (module, uri))
            return True
        # 15分钟之内已经发送过此信息,不再接收此信息,返回False
        else:
            log.info('module %s uri %s have been receive in 15 minutes, last receive time is %s,stop receive it' %
                     (module, uri, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_recv_time[module][uri]))))
            return False

    return False


def check():
    """
    检测报警信息
    :return:
    """
    log.info("begin to check alarm info")
    conn = MySQLdb.connect(
        charset='utf8',
        cursorclass=MySQLdb.cursors.DictCursor,
        host="10.101.1.141",
        user="oc",
        passwd="oc",
        port=3306,
        db="oc"
    )

    latencies = get_latency(conn)
    thresholds = get_threshold(conn)

    for i in latencies:
        if i['pv'] < 10:
            continue
        if i['module'] == 'a1.go2yd.com' and i['pv'] < 100:
            continue

        error_percentage_threshold = 0  # 错误率报警上限
        latency_threshold = 0   # latency报警上限
        # get threshold
        # 第一级匹配，module和uri全部匹配
        for t in thresholds:
            if t['module'].strip() == i['module'].strip() and t['uri'].strip() == i['uri'].strip():
                error_percentage_threshold = t['error_ratio']
                latency_threshold = t['latency']
                break

        # 第二级匹配，module字段匹配且uri字段为空
        if error_percentage_threshold <= 0 or latency_threshold <= 0:
            for t in thresholds:
                if t['module'].strip() == i['module'].strip() and len(t['uri'].strip()) == 0:

                    error_percentage_threshold = t['error_ratio']
                    latency_threshold = t['latency']
                    break

        # 第三级匹配，前两次匹配均失败，则采用默认值
        if error_percentage_threshold <= 0 or latency_threshold <= 0:
            error_percentage_threshold = default_error_percentage_threshold
            latency_threshold = default_latency_threshold

        # 判断是否达到报警条件
        error_ratio = (100 * i['pv_srv_err']) / i['pv']
        can_alarm = False
        if i['pv_srv_err'] > 10 and error_ratio > error_percentage_threshold:
            can_alarm = True
        if i['latency'] > latency_threshold:
            can_alarm = True

        if can_alarm:
            log.info('%s,%s,%d,%.2f,is reach the alarm condition,now we check if it is need to be recv' % (
                i['module'], i['uri'], int(i['latency']), error_ratio))
        else:
            log.debug('********%s,%s,%d,%.2f,is not reach the alarm condition*******' %
                     (i['module'], i['uri'], int(i['latency']), error_ratio))

        need_recv_alarm = need_recv(can_alarm, i['module'], i['uri'])
        # 若达到报警信息,将此信息存放在message字典中
        if need_recv_alarm:
            log.info('%s,%s,%s,%d,%.2f,is reach the alarm condition,now we will receive it' %
                     (i['host'], i['module'], i['uri'], int(i['latency']), error_ratio))

            if i['module'] not in message:
                message[i['module']] = {}
            if i['uri'] not in message[i['module']]:
                message[i['module']][i['uri']] = [i['latency'], error_ratio]

            # 记录此次接收报警信息的时间
            last_recv_time[i['module']][i['uri']] = int(time.time())

    conn.close()


# 将发送短信的报警详细信息插入数据库
def insert_module_alarm(d, moduleAlarm):
    try:
        session = d.db_session()
        session.add(moduleAlarm)
        session.commit()
        session.close()
    except MySQLdb.Error, e:
        log.error('insert module alarm error:%d: %s' % (e.args[0], e.args[1]))


# 从数据库中读取最大的sms_id + 1
def get_max_sms_id(d):
    session = d.db_session()
    max_sms_id = session.query(func.max(ModuleAlarm.sms_id)).first()
    session.close()
    if max_sms_id[0] is None:
        return 0
    return max_sms_id[0] + 1


def send_message():
    """
    # 从message字典中读取报警信息,经过合并发送短信给相关人员
    :return:
    """
    phone_send_record = {}  # 记录模块对应的联系人的发送短信数
    default_send_record = {}  # 记录全局联系人发送短信数

    # 若有报警信息才进行发送短信操作
    if len(message):
        log.info('send message begain')

        dao = Dao()
        conn = MySQLdb.connect(
                charset='utf8',
                cursorclass=MySQLdb.cursors.DictCursor,
                host="10.101.1.141",
                user="oc",
                passwd="oc",
                port=3306,
                db="oc"
        )

        # 按模块进行合并报警信息并发送
        for (module, uri_dict) in message.items():

            send_time = datetime.datetime.now()

            sms_id = get_max_sms_id(dao)
            # 将sms_id转换为36进制,作为短信链接发送给手机
            str_sms_id = ten_to_36(sms_id)

            err_ratio = 0.0
            latency = 0

            # 保存每个module中的第一个uri,用于当仅有一个错误时,发送短信时显示uri.（多个错误时不显示uri,给出url网页链接)
            uri = uri_dict.keys()[0]

            for (uri_item, value) in uri_dict.items():
                # 获取同一模块多个uri错误中的最大延迟和错误率
                if value[0] > latency:
                    latency = value[0]
                if value[1] > err_ratio:
                    err_ratio = value[1]
                # 将每一个module+uri信息都插入数据库,它们的sms_id相同
                moduleAlarm = ModuleAlarm(sms_id, module, uri_item, value[0], float('%.2f' % value[1]), 0, 0, send_time)
                insert_module_alarm(dao, moduleAlarm)

            # 获取联系人
            receivers = get_receiver(conn)

            # 获取模块对应联系人手机号和邮箱号,然后发送短信
            if module in receivers:
                # phone_send_record保存此次循环中向莫个模块的联系人发送的短信条数,用于控制每一分钟发送短信条数
                if module not in phone_send_record:
                    phone_send_record[module] = {}

                phone_list = receivers[module]['phone']
                for phone in phone_list:
                    if phone == '':
                        continue
                    if phone not in phone_send_record[module]:
                        phone_send_record[module][phone] = 0
                    # 超过最大发送短信条数,停止发送短信
                    if phone_send_record[module][phone] > receivers[module]['sms_max']:
                        log.info('[%s][%s] have been send max sms,so stop send this alarm' % (module, phone))
                        continue
                    # 开始发送短信
                    send_sms(phone, module.split('.')[0], len(uri_dict), uri.split('/')[-1], latency, err_ratio, str_sms_id)
                    phone_send_record[module][phone] += 1

            # 向全局联系人发送报警短信
            for phone in default_phones:
                if phone not in default_send_record:
                    default_send_record[phone] = 0
                if default_send_record[phone] > default_sms_max:
                    log.info('[%s][%s] have been send max sms,so stop send this alarm'
                             % (module, phone))
                    continue
                send_sms(phone, module.split('.')[0], len(uri_dict), uri.split('/')[-1], latency, err_ratio, str_sms_id)
                default_send_record[phone] += 1

        # 清空message字典
        message.clear()


if __name__ == '__main__':

    while True:
        check()
        send_message()
        time.sleep(60)


