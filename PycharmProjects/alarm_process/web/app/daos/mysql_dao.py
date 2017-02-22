#!/usr/bin/env python
# -*-coding:utf8-*-

import MySQLdb
import MySQLdb.cursors


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
                host='10.101.1.141',
                user='oc',
                passwd='oc',
                port=3306,
                db='oc'
            )
        except:
            return None
        return conn

    def get_module_alarm_by_smsid(self, sms_id):
        if self.conn is None:
            return []
        sql = 'select * from module_alarm where sms_id = %d' % sms_id

        cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql)
        all_node = [x for x in cursor.fetchall()]
        cursor.close()
        return all_node


if __name__ == '__main__':
    pass
