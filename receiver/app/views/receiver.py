#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'kun'
from flask import render_template, Blueprint, request, redirect, url_for

from app.daos import mysql_dao

blueprint_receiver = Blueprint('receiver', __name__, url_prefix='/receiver', static_folder='static')


@blueprint_receiver.route('/test')
def test():
    return render_template('receiver/test.html')


@blueprint_receiver.route('/', methods=['GET', 'POST'])
@blueprint_receiver.route('/show_receiver', methods=['GET', 'POST'])
def show_receiver():
    mysql_dao_obj = mysql_dao.MysqlDao()
    receiver = mysql_dao_obj.get_receiver()
    return render_template('receiver/show_receiver.html', receiver=receiver)


@blueprint_receiver.route('/delete_email', methods=['GET', 'POST'])
def delete_email():
    email_name = request.form.get('email_list', '')
    module_name = request.form.get('module_name', '')

    mysql_dao_obj = mysql_dao.MysqlDao()
    mysql_dao_obj.delete_email(email_name, module_name)

    return redirect(url_for('receiver.show_receiver'))


@blueprint_receiver.route('/add_email', methods=['GET', 'POST'])
def add_email():
    if request.method == 'POST':
        email_name = request.form.get('email_name', '')
        module_name = request.form.get('module_name', '')
        if email_name and module_name:
            mysql_dao_obj = mysql_dao.MysqlDao()
            if mysql_dao_obj.update_email(module_name, email_name):
                return redirect(url_for('receiver.show_receiver'))
        else:
            return render_template('receiver/show_receiver.html')


@blueprint_receiver.route('/edit', methods=['GET', 'POST'])
def receiver_edit():
    if request.method == 'GET':
        module_name = request.args.get('module_name', '')
        mysql_dao_obj = mysql_dao.MysqlDao()
        module_info = mysql_dao_obj.get_module_info(module_name)

        phone_list = []
        email_list = []
        if module_info:
            phone_str = module_info[0]['phone']
            email_str = module_info[0]['email']

            if phone_str:
                phone_list = phone_str.split(',')
            if email_str:
                email_list = email_str.split(',')

        return render_template('receiver/edit.html', module_info=module_info[0], phone_list=phone_list, email_list=email_list)


if __name__ == '__main__':
    pass
