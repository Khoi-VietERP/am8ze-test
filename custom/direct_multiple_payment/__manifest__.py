# -*- coding: utf-8 -*-
{
    'name': "direct_multiple_payment",

    'summary': """
        direct_multiple_payment
    """,

    'description': """
        direct_multiple_payment
    """,

    'author': "VietERP / Sang",
    'website': "http://www.vieterp.vn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'VietERP',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/multiple_payment.xml',
        'views/sequence.xml',
    ],
}
