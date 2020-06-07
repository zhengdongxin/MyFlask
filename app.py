""" 创建app 并做初始化 """
import os
import ujson as json
from flask import Flask
from flask import request, Response

from flask_mysql import get_db, DatabaseTables, create_table
from api import product
from api import account
from api import order


def create_app():

    app = Flask(__name__)
    flask_config = os.environ.get('FLASK_CONFIG', 'config.BaseConfig')
    app.config.from_object(flask_config)

    app.register_blueprint(product.BP)
    app.register_blueprint(account.BP)
    app.register_blueprint(order.BP)
    app.before_request(before_request)


    return app

def before_request():
    request.return_success = return_success
    request.return_error = return_error

    mysql_conn = get_db()
    request.mysql_conn = mysql_conn
    request.mysql_cursor = mysql_conn.cursor()
    request.mysql = DatabaseTables(mysql_conn)

    #create_table()



def return_success(data='success'):
    res = json.dumps({'code': 0, 'msg': 'success', 'data': data})
    try:
        request.mysql_conn.commit()
    except:
        raise
    return Response(res, mimetype='application/json')


def return_error(code, msg, data=None):
    try:
        request.mysql_conn.rollback()
    except:
        raise
    res = json.dumps({'code': code, 'msg': msg, 'data': data if data else {}})
    return Response(res, mimetype='application/json')