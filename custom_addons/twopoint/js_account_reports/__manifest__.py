# -*- coding: utf-8 -*-menu_finance
{
    'name': 'Accounting Excel Reports',
    'version': '1',
    'category': 'Accounting & Finance',
    'sequence': 15,
    'summary': 'Accounts Reports',
    'description': """
Reports like P&L, BS, Detailed P&L etc.
=======================================

    """,
    'depends': [
        'base', 'account',
    ],
    'data': [
        # 'wizard/iaf_report_view.xml',
        'wizard/js_acc_rept_wiz_view.xml',

        'security/ir.model.access.csv',
        'views/account_account_view.xml',

    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'qweb': [],
}
