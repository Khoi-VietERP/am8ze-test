# -*- coding: utf-8 -*-menu_finance
{
    'name': 'IAF',
    'author': 'Vscale Fusion(Quan)',
    'version': '1.4',
    'category': 'Accounting & Finance',
    'sequence': 75,
    'summary': 'IAF',
    'description': """
IAF (IRAS Audit File ) Report
==========

IAF (IRAS Audit File ) Report in XML and TXT format.
    """,
    'website': 'https://www.vscalefusion.com/',
    'images': [
    ],
    'depends': [
        'base', 'account',
        'sg_account_report','sg_hr_payslip_YTD',
        # 'custom_report_temp',sg_credit_debit_note,
        # 'asme_accounting_excel_reports'

    ],
    'data': [
        'wizards/iaf_report_view.xml',
        'wizards/config_account_iaf_report_view.xml',

        'security/ir.model.access.csv',
        'data/account_financial_report_data.xml',
        'views/inherit_currency_configuration.xml',

    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'qweb': [],
}
