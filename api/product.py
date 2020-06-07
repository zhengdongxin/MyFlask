from datetime import datetime
from flask import Blueprint, request# as context

BP = Blueprint('product_api', __name__)


@BP.route('/api/product/create', methods=['GET'])
def add():
    now = datetime.now()
    def_data = {
        'create_time': now,
        'last_modify_time': now,
        'title': '产品名'
    }
    product_id = request.mysql.product.add(def_data)
    return request.return_error(401, 'error %s' % product_id)
    #return request.return_success(product_id)


@BP.route('/api/product/find', methods=['GET'])
def find():
    query = {
        'query': [{}],
        'lmit': 2,
        'offset': 1,
        'order': 'create_time:+',
        'sum': 'price'
    }
    res = request.mysql.product.find(query)

    return request.return_success(res)

@BP.route('/api/product/<int:product_id>', methods=['GET'])
def get(product_id):
    product = request.mysql.product.get({'i': product_id})
    if not product:
        return request.return_error(404, 'product not exist')
    return request.return_success(product)


@BP.route('/api/product/<int:product_id>/update', methods=['GET'])
def update(product_id):
    product = request.mysql.product.get({'i': product_id})
    if not product:
        return request.return_error(404, 'product not exist')
    
    now = datetime.now()
    def_data = {
        'i': product_id,
        'price': 100,
        'last_modify_time': now
    }
    res = request.mysql.product.post(def_data)
    return request.return_success(res)


def lessen_stock(product_id, num):
    res = request.mysql_cursor.execute('''\
UPDATE product SET stock=stock-%s''', num)
    return res