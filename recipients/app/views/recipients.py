#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'kun'
from flask import render_template, Blueprint, request, redirect, url_for, flash

from app.daos import mysql_dao

blueprint_recipient = Blueprint('recipients', __name__, url_prefix='/recipients', static_folder='static')


@blueprint_recipient.route('/', methods=['GET', 'POST'])
@blueprint_recipient.route('/recipients', methods=['GET', 'POST'])
def show_receiver():
    mysql_dao_obj = mysql_dao.MysqlDao()
    receiver = mysql_dao_obj.get_recipients()
    return render_template('recipients/recipients.html', receiver=receiver)


@blueprint_recipient.route('/contacts')
def show_recipient():
    mysql_dao_obj = mysql_dao.MysqlDao()
    contactlist = mysql_dao_obj.get_contacts()
    return render_template('recipients/contacts.html', contactlist=contactlist)


@blueprint_recipient.route('/add_contacts', methods=['GET', 'POST'])
def add_contacts():
    if request.method == 'GET':
        return render_template('recipients/contacts.html')
    elif request.method == 'POST':
        name = request.form.get('name', '')
        phone = request.form.get('phone', '')
        email = request.form.get('email', '')
        if phone and name:
            try:
                mysql_dao_obj = mysql_dao.MysqlDao()
                mysql_dao_obj.add_contacts(name, phone, email)
            except:
                flash("联系人写入数据库错误!")

            flash("添加联系人成功!")
        else:
            flash('添加联系人错误!手机号和姓名不能为空')

        return redirect('recipients/contacts')


@blueprint_recipient.route('/delete_contacts', methods=['GET', 'POST'])
def delete_contacts():
    if request.method == 'GET':
        phone = request.args.get('phone', '')
        if phone:
            try:
                mysql_dao_obj = mysql_dao.MysqlDao()
                mysql_dao_obj.delete_contacts(phone)
            except:
                flash("从数据库中删除联系人错误!")
            flash('删除联系人成功!')
        else:
            flash('要删除的记录不存在!')
    return redirect('recipients/contacts')


@blueprint_recipient.route('/edit_contacts', methods=['GET', 'POST'])
def edit_contacts():
    if request.method == 'GET':
        phone = request.args.get('phone', '')
        mysql_dao_obj = mysql_dao.MysqlDao()
        contacts = mysql_dao_obj.get_contacts_by_phone(phone)
        return render_template('recipients/edit_contacts.html', contacts=contacts)
    else:
        phone = request.form.get('phone', '')
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        contacts_id = request.form.get('contacts_id', '')
        if phone and name:
            try:
                mysql_dao_obj = mysql_dao.MysqlDao()
                mysql_dao_obj.update_contacts(int(contacts_id), phone, name, email)
            except:
                flash("修改联系人错误!")
                return redirect('recipients/contacts')
            flash('修改联系人成功')
        else:
            flash('要修改的记录不存在')
    return redirect('recipients/contacts')


if __name__ == '__main__':
    pass
