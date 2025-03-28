# -*- coding: utf-8 -*-

{
    'name': 'Customized Invoice Designs',
    'version': '1.0.0.3',
    'summary': """Configurable Customized Invoice Templates""",
    'description': """Configurable Customized Invoice Templates""",
    'category': 'Accounting/Accounting',
    'author': 'iKreative',
    'website': "",
    'license': 'AGPL-3',

    'price': 75.0,
    'currency': 'USD',

    'depends': ['base', 'account',
                'report_utils'
                ],

    'data': [
        'data/reports.xml',
        'report/report_custom_template1.xml',
        'report/report_custom_template2.xml',
        'report/report_invoice.xml',
        'views/config_view.xml',
        'views/reporting_template.xml',
    ],
    'demo': [

    ],
    'images': ['static/description/banner.png'],
    'qweb': [],

    'installable': True,
    'auto_install': False,
    'application': False,
}
