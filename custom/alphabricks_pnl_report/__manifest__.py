# -*- coding: utf-8 -*-
{
    'name': "alphabricks_pnl_report",

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
        'account_dynamic_reports'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pnl_report_view.xml',
        'wizard/pnl_report_wizard.xml',
        'views/pnl_report_pdf.xml',
        'views/pnl_report_pdf_landscape.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}
