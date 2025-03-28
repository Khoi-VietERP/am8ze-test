# -*- coding: utf-8 -*-
{
    'name': "my_picking",

    'summary': """
        my_picking""",

    'description': """
        my_picking
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
        'portal',
        'stock',
        'top_modifier_inventory',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/picking_portal_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
