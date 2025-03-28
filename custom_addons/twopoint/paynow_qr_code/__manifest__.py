# -*- coding: utf-8 -*-
{
    'name': 'Paynow QR code',
    'description': 'Paynow QR code',
    'version': '13.0.1.0.0',
    'author': '',
    'website': '',
    'category': 'Tool',
    'depends': ['account','l10n_sg','sale'],
    'data': [
        'security/view_cost_price.xml',
        'views/res_company_view.xml',
        'views/account_move.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}
