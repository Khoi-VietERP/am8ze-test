# -*- coding: utf-8 -*-
{
    'name': "b20220713_print_invoice",

    'summary': """
        b20220713_print_invoice
    """,

    'description': """
        b20220713_print_invoice
    """,

    'author': "Sang",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base',
        'account'
    ],

    'data': [
        'security/ir.model.access.csv',
        'wizard/tax_invoice_report_popup_views.xml',
        'wizard/cash_sales_report_popup_views.xml',
        'wizard/credit_note_report_popup_views.xml',
        'views/report_tax_invoice.xml',
        'views/report_cash_sales.xml',
        'views/report_credit_note.xml',


    ],
}
