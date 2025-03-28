# -*- coding: utf-8 -*-
{
    'name': "modifier_chart_of_accounts",

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
    'version': '13.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account_dynamic_reports',
        'js_account_reports',
        'sg_account_reports_groupby',
    ],

    # always loaded
    'data': [
        'views/chart_of_accounts_view.xml',
    ],
}
