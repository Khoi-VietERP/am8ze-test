# -*- coding: utf-8 -*-
{
    'name': "h202102879_modifier_gst_f5",

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
        'gst_f5',
        'sg_account_report',
        'alphabricks_modifier_tax',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/gstf5_trans_view.xml',
        'views/gstf5_return_view.xml',
        'views/gstreturn_f5_report_trans_view.xml',
        'views/gstreturn_f5_report_view.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}
