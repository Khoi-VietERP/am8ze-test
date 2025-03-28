# -*- coding: utf-8 -*-
{
    'name': "daa_commission",

    'summary': """
        daa_commission
    """,

    'description': """
        daa_commission
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
        'crm',
        'daa_case',
        'daa_field',
        'daa_agreement',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/daa_case_views.xml',
        'views/daa_agreement_views.xml',
        'views/res_users_views.xml',
        'wizards/co_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
