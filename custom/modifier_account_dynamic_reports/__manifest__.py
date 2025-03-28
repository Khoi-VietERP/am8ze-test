# -*- coding: utf-8 -*-
{
    'name': "modifier_account_dynamic_reports",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Vieterp / Sang",
    'website': "http://www.vieterp.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account_dynamic_reports',
        'modifier_ar_ap_report',
        'dynamic_xlsx',
        'alphabricks_close_financial_year',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/ins_account_financial_report.xml',
        'views/templates.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}
