# -*- coding: utf-8 -*-
{
    'name': "alphabricks_modifier_purchase",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Sang",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'purchase',
        'sr_manual_currency_exchange_rate'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order_view.xml',
    ],
}
