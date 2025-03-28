# -*- coding: utf-8 -*-
{
    'name': "h202_gst_reports_transactions",

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
        'base',
        'sg_account_report',
        'h202102879_modifier_menu',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/gst_trans_tax_code_view.xml',
        'views/gst_trans_account_code_view.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}
