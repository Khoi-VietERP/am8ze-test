# -*- coding: utf-8 -*-
{
    'name': "daa_crm_modifier",

    'summary': """
        daa_crm_modifier
    """,

    'description': """
        daa_crm_modifier
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
        'l10n_sg',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/crm_stage_views.xml',
        'views/crm_lead_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
