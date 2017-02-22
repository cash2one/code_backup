#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'kun'
import time
import datetime
from ConfigParser import SafeConfigParser, Error

import requests
from logger import log


def sync_phone_sms(phone, name, info):
    """
    用于发送短信的接口
    :param phone:接受短信的手机号
    :param name:发生报警的服务:module+uri
    :param info:错误详细信息
    :return:
    """
    req = "http://a4.go2yd.com/Website/message/send-sms?key=a548172fdbe9ff9e754f3251efa92856&" \
          "mobile=86{0}&template=1&param[]={1}&param[]={2}&param[]={3}".format(
            phone, time.strftime("%H:%M"), name, info)
    print datetime.datetime.now(), req
    try:
        r = requests.get(req)
        print datetime.datetime.now(), r.text
        d = r.json()
        if d["code"] != 0:
            print datetime.datetime.now(), d["status"], d["reason"]
            log.error('send message error:'+str(d["status"])+d["reason"])
    except:
        log.error('send message exception:')
        print "send sms exception"


def send_sms(phone, module, err_num, uri, latency, err_ratio, str_sms_id):
    """
    发送短信函数,将错误信息格式化后调用短信接口发送短信
    :param phone: 手机号
    :param module: 模块名称
    :param err_num: 模块对应的报警错误数
    :param uri: 模块的第一个错误uri（每个模块可能有多个uri错误）
    :param latency: 每个模块对应的最大延迟
    :param err_ratio: 每个模块对应的最大错误率
    :param str_sms_id: 每个模块对应的sms_id,同一个模块的sms_id相同
    :return:
    """
    # 当只有一个错误时,格式化错误信息:[模块][错误数][uri]
    if err_num == 1:
        # 由于短信字数限制,当模块名和uri长度超过一定长度时,只显示uri
        if len(module) + len(uri) > 33:
            name = "[{0}]".format(uri[:33])
        else:
            name = "[{0}]{1}".format(module, uri)
        err_info = "{0}ms,{1}%".format(int(latency), float('%.2f' % err_ratio))
        log.info('send message to %s: service:%s,reason:%s' % (phone, name, err_info))
    # 当有多个错误时,格式化错误信息为:[模块][错误数]url
    else:
        # 从配置文件中读取send_url,用于控制发送短信时是否发送url链接
        cf = SafeConfigParser()
        cf.read("alarm_process.conf")
        try:
            send_url = cf.get('module_alarm', 'send_url')
        # 若读取配置文件发生异常时,置send_url为True,默认发送链接
        except Error:
            log.error('read send_url from conf error')
            send_url = False
        # 若需要发送url链接,将从配置文件中读取host_ip生成url短链接
        if send_url is True:
            try:
                host_ip = cf.get('module_alarm', 'host_ip')
                port = cf.get('module_alarm', 'port')
            except Error:
                log.error('read host ip from conf file error')
                host_ip = '10.111.0.12'
                port = '9100'

            err_info = "[{0}ms,{1}%]http://{2}:{3}/?{4}".format(
                    int(latency), float('%.2f' % err_ratio), host_ip, port, str_sms_id)
        # 不需要发送url链接,则只给出错误率和延迟
        else:
            err_info = "{0}ms,{1}%".format(int(latency), float('%.2f' % err_ratio))

        name = "[{0}]{错误数:1}".format(module, err_num)

        log.info('send message to %s: service:%s,reason:%s' % (phone, name, err_info))

    sync_phone_sms(phone, name, err_info)


if __name__ == '__main__':
    pass