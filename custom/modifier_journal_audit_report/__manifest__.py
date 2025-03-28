# -*- coding: utf-8 -*-
{
    'name': "modifier_journal_audit_report",

    'summary': """
        modifier_journal_audit_report
    """,

    'description': """
        modifier_journal_audit_report
    """,

    'author': "Sang",
    'website': "",
    'category': '',
    'version': '13.0.0.1',
    'depends': [
        'base',
        'sg_account_report',
    ],
    'qweb': [
        'static/src/xml/view.xml',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/journal_audit_report_views.xml',
    ],
    'qweb': ['static/src/xml/view.xml'],
}
