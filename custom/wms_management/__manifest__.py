# -*- coding: utf-8 -*-
{
    'name': "wms_management",

    'summary': """
        wms_management
    """,

    'description': """
        wms_management
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
        'stock',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/wms_plan_views.xml',
        'views/wms_budget_views.xml',
        'views/wms_distance_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
