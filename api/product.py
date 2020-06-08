from datetime import datetime
from flask import Blueprint, request# as context

BP = Blueprint('product_api', __name__)


@BP.route('/api/product/create', methods=['GET'])
def add():
    args = dict(request.args)
    now = datetime.now()
    reset_data = {
        'create_time': now,
        'last_modify_time': now
    }
    args.update(reset_data)
    new_i = request.mysql.product.add(args)
    return request.return_success(new_i)


@BP.route('/api/product/find', methods=['GET'])
def find():
    '''
        query:                     必填
        fields: [字段1,字段2....]   选填
    '''
    args = dict(request.args)
    query = {
        'query': [{
            'stock@min': 17,
            'state@non': [0, 1],
            'price': 100
        }],
        'limit': args.get('limit', 10),
        'offset': args.get('limit', 0),
        'order': 'create_time:-',
        'sum': ['price']
    }
    res = request.mysql.product.find(query)

    return request.return_success(res)

@BP.route('/api/product/info', methods=['GET'])
def get():
    '''
        i: 主键                    必填
        fields: [字段1,字段2....]   选填
    '''
    args = dict(request.args)
    product = request.mysql.product.get(args)
    if not product:
        return request.return_error(404, 'product not exist')
    return request.return_success(product)


@BP.route('/api/product/update', methods=['GET'])
def update():
    '''
        i: 主键                    必填
        其他修改字段选填
    '''
    args = dict(request.args)
    product = request.mysql.product.get({'i': args['i']})
    if not product:
        return request.return_error(404, 'product not exist')

    now = datetime.now()
    reset_data = {
        'last_modify_time': now
    }
    args.update(reset_data)
    res = request.mysql.product.update(args)
    return request.return_success(res)


##############################内部调用###########################################
def lessen_stock(product_i, num):
    res = request.mysql_cursor.execute('''\
UPDATE product SET stock=stock-%s''', num)
    return res
