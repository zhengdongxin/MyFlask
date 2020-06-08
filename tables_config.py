def get_table(name):
    for t in TABLES:
        if name == t['table_name']:
            return t
    return

TABLES = [
    {
        'table_name': 'product',
        'fields': [
            {
                'column_name': 'create_time',
                'type': 'DATETIME',
                'is_index': True
            },{
                'column_name': 'last_modify_time',
                'type': 'DATETIME',
                'is_not_null': False,
                'is_index': True
            },{
                'column_name': 'title',
                'type': 'varchar(100)',
                'default': ''
            },{
                'column_name': 'stock',
                'type': 'INT',
                'default': 0
            },{
                'column_name': 'price',
                'type': 'BIGINT',
                'is_index': True,
                'default': 0
            },{
                'column_name': 'state',
                'type': 'INT',
                'default': 0
            }
        ]
    },{
        'table_name': 'orders',
        'fields': [
            {
                'column_name': 'create_time',
                'type': 'DATETIME',
                'is_index': True
            },{
                'column_name': 'last_modify_time',
                'type': 'DATETIME',
                'is_index': True
            },{
                'column_name': 'order_no',
                'type': 'varchar(100)',
                'is_unique': True,
                'default': ''
            },{
                'column_name': 'account_i',
                'type': 'BIGINT',
                'is_index': True,
                'default': 0
            },{
                'column_name': 'product_i',
                'type': 'BIGINT',
                'is_index': True,
                'default': 0
            },{
                'column_name': 'product_title',
                'type': 'varchar(100)',
                'default': ''
            },{
                'column_name': 'product_price',
                'type': 'BIGINT',
                'default': 0
            },{
                'column_name': 'item_num',
                'type': 'INT',
                'default': 0
            },{
                'column_name': 'amount',
                'type': 'BIGINT',
                'is_index': True,
                'default': 0
            },{
                'column_name': 'state',
                'type': 'INT',
                'default': 0
            }
        ]
    },{
        'table_name': 'account',
        'fields': [
            {
                'column_name': 'create_time',
                'is_index': True,
                'type': 'DATETIME'
            },{
                'column_name': 'last_modify_time',
                'is_index': True,
                'type': 'DATETIME',
            },{
                'column_name': 'name',
                'type': 'varchar(100)',
                'default': ''
            }
        ]
    }
]