# -*- coding: utf-8 -*-
{
    'name': "h202_modifier_accounting",

    'summary': """
        Modifier Accounting
    """,
    'author': "Sang",
    'website': "http://www.yourcompany.com",
    'category': 'Accounting',
    'version': '13.0.0.1',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/account_tax_view.xml',
    ],
}
