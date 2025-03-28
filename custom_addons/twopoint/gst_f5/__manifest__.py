# -*- coding: utf-8 -*-
{
    'name': 'GST F5',
    'author': 'Vscale Fusion',
    'version': '1.4.0',
    'category': 'Vscale (Doan)',
    'sequence': 95,
    'summary': 'GST F5',
    'description': """
GST Feature and Reports
=======================

GST Feature
- Report for GST F5, GST F5 with transactions and GST F8.
- GST Notification for company.
    """,
    'website': 'https://www.vscalefusion.com',
    'depends': [
        'base','account',
        'sg_account_report',
    ],
    'data': [
        # Data
        'data/user_gst.xml',
        'data/channel_data.xml',
        'data/function_data.xml',
        'data/setup.xml',
        'data/import_tax_code.xml',
        # Views
        'views/inherit_view_company_form.xml',
        'views/account_invoice_report_view.xml',
        'views/gstreturn_f8_report_view.xml',
        'views/gstreturn_f5_report_view.xml',
        'views/gstreturn_f5_report_trans_view.xml',
        'views/account.move.xml',
        'views/report_menu.xml',
        'wizards/gstreturnf8_view.xml',
        'wizards/gstreturnf5_trans_view.xml',
        # Security
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
