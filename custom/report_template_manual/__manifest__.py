# -*- coding: utf-8 -*-
{
    'name': "report_template_manual",

    'summary': """
        report_template_manual""",

    'description': """
        report_template_manual
    """,

    'author': "Sang",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'report_utils',
        'report_template_invoice',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/quotation_custom_template.xml',
        'views/custom_template_view.xml',
        'report/custom_template_report.xml',
    ],
}
