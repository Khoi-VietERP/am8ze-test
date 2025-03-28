# -*- coding: utf-8 -*-
{
    'name': "create_ms_word_report",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Sang",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'populating_ms_word_template_modifier',
        'sg_account_report',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/report.xml',
        # 'views/account_aged_trial_balance_view.xml',
    ],
}
