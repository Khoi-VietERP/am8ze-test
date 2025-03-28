# -*- coding: utf-8 -*-
{
    'name': "a5oct2021_modifier_invoicing",

    'summary': """
        a5oct2021_modifier_invoicing
    """,
    'author': "Vieterp / Sang",
    'website': "http://www.vieterp.net",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': [
        'base',
        'account',
        'sg_bank_reconcile',
        'l10n_sg',
        'sr_manual_currency_exchange_rate',
        'mail',
        'base_import',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'security/res_groups.xml',
        'views/account_move_view.xml',
        'views/bank_acc_rec_statement.xml',
        'views/pnl_detail_report.xml',
        'views/account_account_view.xml',
        'views/account_payment_view.xml',
        'views/account_invoice_send_view.xml',
    ],
}
