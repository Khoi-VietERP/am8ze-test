# -*- coding: utf-8 -*-
{
    'name': "top_modifier_user",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "VietERP / Sang",
    'website': "http://www.vieterp.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'ordering_e_commerce',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_users_view.xml',
    ],
    'installable' : True
}
