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
                host='localhost',
                user='root',
                passwd='0411',
                port=3306,
                db='oc'
            )
        except:
            return None
        return conn

    def get_receiver(self):
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

    def update_email(self, module_name, email_name):
        if self.conn is None:
            return []

        try:
            sql = "select email from latency_monitor_recipient where module = '%s' " % module_name
            cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(sql)
            old_email = cursor.fetchall()
            cursor.close()

            if len(old_email[0]['email']):
                new_email = old_email[0]['email']+','+email_name
            else:
                new_email = email_name
            sql2 = "update latency_monitor_recipient set email = '%s' where module = '%s'" % (new_email, module_name)
            cursor2 = self.conn.cursor()
            cursor2.execute(sql2)
            self.conn.commit()
            cursor2.close()
        except:
            print 'update email dao error'
            return False
        return True

    def delete_email(self, email_name, module_name):
        if self.conn is None:
            return False
        try:
            sql = "select email from latency_monitor_recipient where module = '%s' " % module_name
            cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(sql)
            old_email = cursor.fetchall()
            cursor.close()

            email_list = old_email[0]['email'].split(',')
            print email_list



            """
            if len(old_email[0]['email']):
                new_email = old_email[0]['email'] + ',' + email_name
            else:
                new_email = email_name
            sql2 = "update latency_monitor_recipient set email = '%s' where module = '%s'" % (new_email, module_name)
            cursor2 = self.conn.cursor()
            cursor2.execute(sql2)
            self.conn.commit()
            cursor2.close()
            """
        except:
            print 'update email dao error'
            return False
        return True


if __name__ == '__main__':
    d = MysqlDao()
    print d.get_module_info("NewsRecommender")
