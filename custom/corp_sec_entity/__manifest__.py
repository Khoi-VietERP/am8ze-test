# -*- coding: utf-8 -*-
{
    'name': "corp_sec_entity",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'project',
    ],

    # always loaded
    'data': [
        'data/entity_data.xml',
        'security/ir.model.access.csv',
        'views/entity_views.xml',
        'views/tasks_activity_views.xml',
        'views/configuration_views.xml',
        'views/corp_contact_view.xml',
        'views/contact_configuration_view.xml',
    ],
}
