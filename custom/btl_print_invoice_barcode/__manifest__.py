# -*- coding: utf-8 -*-
{
    'name': "btl_print_invoice_barcode",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Sang",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'delivery',
    ],

    'data': [
        'security/ir.model.access.csv',
        'wizard/tax_invoice_barcode_report_popup_views.xml',
        'wizard/credit_note_barcode_report_popup_views.xml',
        'views/report_tax_invoice_barcode.xml',
        'views/report_credit_note_barcode.xml',
        'views/account_move_views.xml',
    ],
}
