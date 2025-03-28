# -*- coding: utf-8 -*-
{
    'name': "alphabricks_statement_of_accounts",

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
        'account_statement',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/statement_of_accounts_report.xml',
        'views/supplier_statement_report.xml',
        'views/customer_statement_report.xml',
        'views/res_partner_view.xml',
    ],
}
