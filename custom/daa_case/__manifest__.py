# -*- coding: utf-8 -*-
{
    'name': "daa_case",

    'summary': """
        daa_case
    """,

    'description': """
        daa_case
    """,

    'author': "DAA / Sang",
    'website': "http://www.daa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'DAA',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'contacts',
        'hr',
        'document_management',
        'daa_agreement',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/daa_case_views.xml',
        'views/res_users_views.xml',
        'views/dunning_letter_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
