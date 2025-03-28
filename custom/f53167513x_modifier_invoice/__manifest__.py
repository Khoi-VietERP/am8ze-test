# -*- coding: utf-8 -*-
{
    'name': "f53167513x_modifier_invoice",

    'summary': """
        Invoice PDF report  
    """,
    'author': "Sang",
    'website': "",
    'category': 'Uncategorized',
    'version': '13.0.0.1',
    'depends': [
        'account',
        'mass_payments_for_multiple_vendors_customers',
        'paynow_qr_code',
    ],
    'data': [
        'report/modifier_external_layout_template.xml',
        'report/music_academy_report.xml',
        'views/invoice_view.xml',
        'views/account_invoice_send_view.xml',
        'views/account_payment_method_view.xml',
        'views/chart_of_accounts_view.xml',
    ],
}
