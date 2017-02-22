#!/usr/bin/env python
# -*-coding:utf8-*-
__author__ = 'Kairong'
import time,MySQLdb
conn = MySQLdb.connect(host='10.101.1.140', user='worker', passwd='services', db='machine_manage_db', charset='utf8')

def sql_one(sql):
    # time.sleep(1)
    try:
        sql_cursor= conn.cursor()
        n =  sql_cursor.execute(sql)
        n_row =  sql_cursor.fetchall()[0]
    finally:
        sql_cursor.close()
    return n_row

def check_top(row):
    namespace_id, parent, des, type = row
    if parent == -1:
        return False
    else:
        return True

def check_out_p(row):
    global tag
    namespace_id, parent, des, type = row
    tag = str(des) + "||"+ tag
    if check_top(row):
        sql = "select * from machine_manage_db.namespace where namespace_id = %d" %(parent,)
        n_row = sql_one(sql)
        check_out_p(n_row)
    return tag

try:
    sql_cmd = conn.cursor()
    sql = 'SELECT * FROM machine_manage_db.namespace where type = "leaf"; '
    n = sql_cmd.execute(sql)
    r_dict = {}
    for row in sql_cmd.fetchall():
        tag = ""
        namespace_id = row[0]
        machine_list = []
        machine_sql = "select inner_ip from machine_manage_db.machine where machine_id in (select machine_id from machine_manage_db.namespace_machine_relation where namespace = %d);" % (namespace_id,)
        mn = sql_cmd.execute(machine_sql)
        for machine_row in sql_cmd.fetchall():
            machine_list.append(machine_row[0])
        tag = check_out_p(row)
        r_tag  = tag.rstrip("||")
        r_dict[r_tag] = machine_list
finally:
    sql_cmd.close()

try:
    sql_cmd = conn.cursor()
    clean_old_sql = "delete from machine_manage_db.srv_machine"
    sql_cmd.execute(clean_old_sql)
    for k,v in r_dict.items():
        for m in v:
            machine_port = m.split(":")
            if len(machine_port) == 2:
                machine_ip, port = machine_port
            else:
                machine_ip, port = str(machine_port[0]), "noport"
            insert_sql = "insert into machine_manage_db.srv_machine(srv_name, machine, port) values('%s', '%s', '%s')" % (k, machine_ip, port)
            # print insert_sql
            sql_cmd.execute(insert_sql)
finally:
    conn.commit()
    sql_cmd.close()
