# -*- coding:utf-8 -*-
import random
import tables_config
from datetime import datetime

import os
import pymysql
import threading
from flask import current_app

MDBN = 'dev'
THREAD_LOCAL = threading.local()

def get_db(prefix=''):
    """ 根据指定前缀申请一个连接， 如果连接断开就自动重连 """
    db_conn = 'db_conn' if not prefix else '-'.join([prefix, 'db_conn'])
    if not hasattr(THREAD_LOCAL, db_conn):
        connect_config = {
            "host": current_app.config['MYSQL_HOST'],
            "port": current_app.config['MYSQL_PORT'],
            "user": current_app.config['MYSQL_USER'],
            "passwd": current_app.config['MYSQL_PASSWORD'],
            "db": current_app.config['MYSQL_DB'],
            "charset": current_app.config['MYSQL_CHARSET'],
            #"autocommit": True
        }
        conn = pymysql.connect(**connect_config)

        setattr(THREAD_LOCAL, db_conn, conn)
    else:
        getattr(THREAD_LOCAL, db_conn).ping(True)

    return getattr(THREAD_LOCAL, db_conn)


def create_database(dbname=MDBN):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('CREATE DATABASE IF NOT EXISTS %s' % dbname)
    conn.commit()


def create_table():
    conn = get_db()
    cur = conn.cursor()
    pkey = 'i'
    tabels = tables_config.TABLES
    for tb in tabels:
        cur.execute('\
CREATE TABLE IF NOT EXISTS %s (%s bigint auto_increment, PRIMARY KEY (%s))\
engine=InnoDB default charset=utf8;' % (tb['table_name'], pkey, pkey))
        if tb.get('snapshot_template'):
            for template in tabels:
                if template['table_name'] == tb['snapshot_template']:
                    fields = template['fields']
            fields = fields + tb['fields']
        else:
            fields = tb['fields']
        for field in fields:
            column_name = field['column_name']
            cur.execute('\
select count(*) from information_schema.columns where table_schema="%s" and \
table_name = "%s" and column_name = "%s";' % (
                MDBN, tb['table_name'], column_name))
            res = cur.fetchone()
            unique = is_not_null = default = index = ''
            if res[0] == 0:
                if field.get('is_unique'):
                    unique = 'unique'
                elif field.get('is_index'):
                    index = ', ADD INDEX {0} ({0})'.format(column_name)
                if field.get('is_not_null', True):
                    is_not_null = 'NOT NULL'
                if field.get('default') != None:
                    default = 'default "%s"' % (field['default'])
                cur.execute('ALTER TABLE %s ADD %s %s %s %s %s %s' %
                    (
                        tb['table_name'],
                        column_name,
                        field['type'],
                        is_not_null,
                        default,
                        unique,
                        index
                    )
                )
    conn.commit()

class DatabaseTable():
    def __init__(self, cursor, table_name, pkey='i'):
        self.pkey = pkey
        self.cursor = cursor
        self.table_name = table_name
        self.table = table = tables_config.get_table(table_name)
        template_table = None
        if table.get('snapshot_template'):
            template_tbname = table['snapshot_template']
            template_table = tables_config.get_table(template_tbname)
        columns = [pkey]
        for f in table['fields']:
            columns.append(f['column_name'])
        if template_table:
            for f in template_table['fields']:
                columns.append(f['column_name'])
        self.columns = columns


    def add(self, args):
        columns = self.columns
        tbname  = self.table_name
        cur     = self.cursor
        set_data = []
        set_fields = []
        for k in args:
            if k in columns:
                set_data.append(args.get(k))
                set_fields.append(k)
        field_str = ', '.join(set_fields)
        rep_str = ', '.join(['%s'] * len(set_fields))
        sql = 'INSERT INTO {0} ({1}) VALUES ({2});'.format(
            tbname, field_str, rep_str)
        cur.execute(sql, tuple(set_data))
        return cur.lastrowid

    def get(self, args):
        pkey = self.pkey
        tbname = self.table_name
        columns = self.columns
        fields = args.get('fields', columns)
        cur = self.cursor
        sql = 'SELECT {0} FROM {1} WHERE {2}=%s;'.format(
            ', '.join(fields), tbname, pkey)
        cur.execute(sql, (args[pkey], ))
        row = cur.fetchone()
        if not row:
            return
        item = {}
        for i, field in enumerate(fields):
            if isinstance(row[i], datetime):
                item[field] = str(row[i])
            else:
                item[field] = row[i]
        return item

    def delete(self, args):
        pkey = self.pkey
        tbname = self.table_name
        cur = self.cursor
        cur.execute('DELETE FROM {} WHERE {}=%s'.format(
            tbname, pkey), (args['i'], ))
        return cur.rowcount

    def update(self, args):
        cur = self.cursor
        pkey = self.pkey
        columns = self.columns
        tbname = self.table_name
        set_data = []
        set_columns = []
        for f in columns:
            if f in args and f != pkey:
                set_columns.append('{}=%s'.format(f))
                set_data.append(args[f])
        set_data.append(args[pkey])
        set_data = tuple(set_data)
        cur.execute('UPDATE {} SET {} WHERE {}=%s;'.format(
            tbname, ','.join(set_columns), pkey), set_data)
        return cur.rowcount

    def updatemany(self, args):
        cur = self.cursor
        columns = self.columns
        tbname = self.table_name
        or_str = ''
        or_list = []
        query_val = []

        set_data = []
        set_columns = []
        for qr in args['where']:
            and_str = ''
            and_list = []
            for field, val in qr.items():
                if '@' in field:
                    key, type_ = field.split('@')
                    if type_ in ['max', 'min']:
                        map_ = {'max': '<', 'min': '>='}
                        and_list.append('{0}{1}%s'.format(key, map_[type_]))
                        query_val.append(val)
                    if type_ == 'like':
                        and_list.append('{0} LIKE %s'.format(key))
                        _str = '%{0}%'.format(val)
                        query_val.append(_str)
                    elif type_ == 'in':
                        len_ = len(val)
                        if len_ > 0:
                            s_str = ','.join(['%s'] * len_)
                            _str = '{0} IN ({1})'.format(key, s_str)
                            and_list.append(_str)
                            query_val = query_val + val
                    elif type_ == 'non':
                        s_str = ','.join(['%s'] * len(val))
                        _str = '{0} NOT IN ({1})'.format(key, s_str)
                        and_list.append(_str)
                        query_val = query_val + val
                else:
                    and_list.append('{0}=%s'.format(field))
                    query_val.append(val)
            if len(and_list):
                and_str = '({0})'.format(' AND '.join(and_list))
                or_list.append(and_str)
        if len(or_list):
            or_str = 'WHERE {0}'.format(' OR '.join(or_list))
        for f in columns:
            if f in args and f != 'where':
                set_columns.append('{}=%s'.format(f))
                set_data.append(args[f])
        set_data = tuple(set_data + query_val)
        cur.execute('UPDATE {} SET {} {};'.format(
            tbname, ','.join(set_columns), or_str), set_data)
        return cur.rowcount

    def find(self, args):
        cur = self.cursor
        columns = self.columns
        fields = args.get('fields', columns)
        tbname = self.table_name
        order_column, desc = args.get('order', 'i:-').split(':')
        desc = 'DESC' if desc == '-' else ''
        offset = args.get('offset', 0)
        limit = args.get('limit', 10)
        assert limit <= 99999, 'limit over 1000: %s' % limit
        or_str = ''
        or_list = []
        query_val = []
        for qr in args['query']:
            and_str = ''
            and_list = []
            for field, val in qr.items():
                if '@' in field:
                    key, type_ = field.split('@')
                    if key not in columns:
                        continue
                    if type_ in ['max', 'min']:
                        map_ = {'max': '<', 'min': '>='}
                        and_list.append('{0}{1}%s'.format(key, map_[type_]))
                        query_val.append(val)
                    if type_ == 'like':
                        and_list.append('{0} LIKE %s'.format(key))
                        _str = '%{0}%'.format(val)
                        query_val.append(_str)
                    elif type_ == 'in':
                        len_ = len(val)
                        if len_ > 0:
                            s_str = ','.join(['%s'] * len_)
                            _str = '{0} IN ({1})'.format(key, s_str)
                            and_list.append(_str)
                            query_val = query_val + val
                    elif type_ == 'non':
                        s_str = ','.join(['%s'] * len(val))
                        _str = '{0} NOT IN ({1})'.format(key, s_str)
                        and_list.append(_str)
                        query_val = query_val + val
                else:
                    if field not in columns:
                        continue
                    and_list.append('{0}=%s'.format(field))
                    query_val.append(val)
            if len(and_list):
                and_str = '({0})'.format(' AND '.join(and_list))
                or_list.append(and_str)
        if len(or_list):
            or_str = 'WHERE {0}'.format(' OR '.join(or_list))
        cur.execute('''\
SELECT COUNT(*) FROM {0} {1};'''.format(tbname, or_str), tuple(query_val))
        total = cur.fetchone()[0]
        if total < int(limit):
            limit = total
        query = tuple(query_val + [int(limit), int(offset)])
        cur.execute('''\
SELECT {0} FROM {1} {2} ORDER BY {3} {4} LIMIT %s OFFSET %s;'''.format(
            ', '.join(fields), tbname, or_str, order_column, desc), query)
        rows = cur.fetchall()
        items = []
        for db_data in rows:
            item = {}
            for i, field in enumerate(fields):
                if isinstance(db_data[i], datetime):
                    item[field] = str(db_data[i])
                else:
                    item[field] = db_data[i]
            items.append(item)
        res = {'total' : total, 'list' : items, 'sum': {}}
        if args.get('sum'):
            for column in args['sum']:
                if column in columns:
                    cur.execute('''\
SELECT SUM({0}) FROM {1} {2};'''.format(column, tbname, or_str), query[:-2])
                    total_sum = cur.fetchone()
                    t = int(total_sum[0] or 0)
                    res['sum'][column] = t
        return res

class DatabaseTables():
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        for tem in tables_config.TABLES:
            tb = DatabaseTable(self.cursor, tem['table_name'])
            setattr(self, tem['table_name'], tb)

    def drop_column(self, tbname, column):
        cur = self.cursor
        cur.execute('''\
ALTER TABLE {0} DROP COLUMN {1};'''.format(tbname, column))
        return

    def drop_table(self, tbname):
        cur = self.cursor
        cur.execute('''DROP TABLE IF EXISTS {0};'''.format(tbname))
        return

    def create_code(self, id_, width=12, prefix='', suffix='',
                    insert_date=False):
        id_len = len(str(id_))
        random_len = width-id_len-len(str(id_len))-len(prefix)-len(suffix)
        date = ''
        if insert_date:
            now = datetime.now()
            date = '{:0>2}{:0>2}{:0>2}'.format(str(now.year)[-2:],now.month,1)
            random_len = random_len - len(date)
        assert 70 > random_len > 0, 'width error: %s' % random_len
        char = [str(i) for i in range(10)] * 7
        ran_str = ''.join(random.sample(char, random_len))
        i_num = '{}{}{}{}{}{}'.format(prefix,date,id_len,ran_str,id_,suffix)
        return i_num

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
