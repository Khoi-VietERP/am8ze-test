# -*- coding: utf-8 -*-
{
    'name': "daa_field",

    'summary': """
        daa_field
    """,

    'description': """
        daa_field
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
        'mail',
        'daa_case',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/mail_activity_views.xml',
        'views/daa_case_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
