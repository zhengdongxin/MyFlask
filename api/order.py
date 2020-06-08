from datetime import datetime
from flask import Blueprint, request
from api.product import lessen_stock

BP = Blueprint('order_api', __name__)


@BP.route('/api/order/create', methods=['GET'])
def add():
    '''
        num: 购买数量
        product_i： 产品主键
        account_i： 用户主键
    '''
    args = dict(request.args)
    num = int(args.get('num', 0))

    product = request.mysql.product.get({'i': args['product_i']})
    if not product:
        return request.return_error(404, 'product not exist')
    if product['state'] == 0:
        return request.return_error(404, '产品已下架')
    if product['stock'] - num <= 0:
        return request.return_error(404, '产品库存不足')

    account = request.mysql.account.get({'i': args['account_i']})
    if not account:
        return request.return_error(1404, 'account not exist')

    # 减少库存
    lessen_stock(args['product_i'], num)

    now = datetime.now()
    add_order_data = {
        'create_time': now,
        'last_modify_time': now,
        'account_i': args['account_i'],
        'product_i': args['product_i'],
        'item_num': num,
        'amount': num * product['price'],
        'product_title': product['title'],
        'product_price': product['price']
    }
    order_i = request.mysql.orders.add(add_order_data)
    order_no = request.mysql.create_code(order_i)

    update_data = {
        'i': order_i,
        'order_no': order_no
    }
    request.mysql.orders.update(update_data)
    return request.return_success(order_i)
