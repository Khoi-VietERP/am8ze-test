# -*- coding: utf-8 -*-
{
    'name': "redirect_internal_only",

    'summary': """
        redirect_internal_only
    """,

    'description': """
        redirect_internal_only
    """,

    'author': "Am8ze / Sang",
    'website': "http://www.am8ze.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Am8ze',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'website',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
}
