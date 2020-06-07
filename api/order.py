from datetime import datetime

from flask import Blueprint, request

BP = Blueprint('order_api', __name__)

from api.product import lessen_stock

@BP.route('/api/order/create', methods=['GET'])
def add():
    account_id = request.args.get('account_id')
    product_id = request.args.get('product_id')
    num = int(request.args.get('num', 0))

    product = request.mysql.product.get({'i': product_id})
    if not product:
        return request.return_error(404, 'product not exist')
    if product['state'] == 0:
        return request.return_error(404, '产品已下架')
    if product['stock'] <= 0:
        return request.return_error(404, '产品库存不足')

    account = request.mysql.account.get({'i': account_id})
    if not account:
        return request.return_error(1404, 'account not exist')

    # 减少库存
    lessen_stock(product_id, num)

    now = datetime.now()
    add_order_data = {
        'create_time': now,
        'last_modify_time': now,
        'account_id': account_id,
        'product_id': product_id,
        'item_num': num,
        'amount': num * product['price'],
        'product_title': product['title'],
        'product_price': product['price']
    }
    print(add_order_data)
    order_id = request.mysql.orders.add(add_order_data)
    return request.return_success(order_id)