# -*- coding: utf-8 -*-
{
    'name': "h202_modifier_invoice_sequence",

    'summary': """
        Modifier Sequence
    """,
    'author': "Sang",
    'category': 'Accounting',
    'version': '13.0.0.1',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/ir_sequence_views.xml',
        'views/account_move_views.xml',
    ],
}
