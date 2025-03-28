# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).
{
    'name': 'Sale Return',
    'version': '1.0',
    "summary": '',
    'description': """""",
    'category': 'Sales/Sales',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'images': ['static/description/banner.jpg'],
    'depends': ['sale_management', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/return_sequence_data.xml',
        'wizard/knk_sale_return_wizard_views.xml',
        'views/sale_views.xml',
        'views/sale_order_return_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'currency': 'EUR',
    'price': 30,
}
