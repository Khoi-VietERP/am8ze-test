# -*- coding: utf-8 -*-
{
    'name': "daa_datapost",

    'summary': """
        daa_datapost
    """,

    'description': """
        daa_datapost
    """,

    'author': "DAA / Sang",
    'website': "http://www.daa.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'l10n_sg',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'qweb': ['static/src/xml/account_invoice.xml'],
    'installable': True,
}
