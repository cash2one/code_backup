#!/usr/bin/env python
# -*-coding:utf8-*-

import MySQLdb
import MySQLdb.cursors
from flask import flash


class MysqlDao:
    conn = None

    def __init__(self):
        self.conn = self.__connect_database()
        if self.conn is None:
            print "connect to mysql failed"

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    @staticmethod
    def __connect_database():
        try:
            conn = MySQLdb.connect(
                charset='utf8',
                cursorclass=MySQLdb.cursors.DictCursor,
                host='localhost',
                user='root',
                passwd='0411',
                port=3306,
                db='oc'
            )
        except:
            return None
        return conn

    def get_recipients(self):
        if self.conn is None:
            return []
        sql = 'select * from latency_monitor_recipient'

        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        all_node = [x for x in cursor.fetchall()]
        cursor.close()
        return all_node

    def get_module_info(self, module_name):
        if self.conn is None:
            return []
        sql = "select * from latency_monitor_recipient where module = '%s' " % module_name

        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_contacts(self):
        if self.conn is None:
            return []
        sql = 'select * from contacts'

        cursor = self.conn.cursor()
        cursor.execute(sql)
        all_node = cursor.fetchall()
        cursor.close()
        return all_node

    def get_contacts_by_phone(self, phone):
        if self.conn is None:
            return
        sql = "select * from contacts where phone='%s'" % phone

        cursor = self.conn.cursor()
        cursor.execute(sql)
        contacts = cursor.fetchone()
        cursor.close()
        return contacts

    def add_contacts(self, name, phone, email):
        if self.conn is None:
            return []
        sql = "insert into contacts(phone, name, email) VALUES ('%s','%s','%s')" % (phone, name, email)

        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def delete_contacts(self, phone):
        if self.conn is None:
            return []
        sql = "delete from contacts where phone='%s' " % phone
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def update_contacts(self, contacts_id, phone, name, email):
        if self.conn is None:
            return
        sql = "update contacts set phone='%s', name='%s', email='%s' where id='%d' " % (phone, name, email, contacts_id)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()


if __name__ == '__main__':
    d = MysqlDao()
    d.update_contacts(1,'13297028626', 'zhangkun2', '123')
