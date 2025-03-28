# -*- coding: utf-8 -*-
{
    'name': "odoo_integrate_iras_api",

    'summary': """
        odoo_integrate_iras_api
    """,

    'description': """
        odoo_integrate_iras_api
    """,

    'author': "Am8ze / Sang",
    'website': "http://www.am8ze.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Am8ze',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sg_income_tax_report',
        'sg_appendix8a_report',
        'sg_appendix8b_report',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/iras_api_config_view.xml',
        'views/iras_api_config_data.xml',
        'views/iras_api_submit_view.xml',
        'views/binary_ir8a_text_file_view.xml',
        'views/binary_ir8s_text_file_view.xml',
        'views/binary_appendix8a_text_file_view.xml',
        'views/binary_appendix8b_text_file_view.xml',
    ],
}
