# -*- coding: utf-8 -*-
{
    'name': "daa_contact_modifier",

    'summary': """
        daa_contact_modifier
    """,

    'description': """
        daa_contact_modifier
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
        'daa_case',
        'daa_agreement',
        'daa_field',
        'daa_commission',
        'l10n_sg',
    ],

    # always loaded
    'data': [
        'data/industry_code.xml',
        'data/partner_status.xml',
        'security/ir.model.access.csv',
        'views/industry_code_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/daa_case_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
