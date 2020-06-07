from datetime import datetime

from flask import Blueprint, request


BP = Blueprint('account_api', __name__)


@BP.route('/api/account/create', methods=['GET'])
def add():
    now = datetime.now()
    def_data = {
        'create_time': now,
        'last_modify_time': now,
        'name': request.args.get('name', '默认用户名')
    }
    account_id = request.mysql.account.add(def_data)
    return request.return_success(account_id)