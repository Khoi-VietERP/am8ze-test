# -*- coding: utf-8 -*-
{
    'name': "corp_sec_entity_history",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Vieterp / Sang",
    'website': "http://www.vieterp.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'corp_sec_entity'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/entity_view.xml',
        'views/history_register_of_members_view.xml',
        'views/history_register_of_applications_view.xml',
        'views/register_of_auditors_view.xml',
        'views/history_register_of_beneficial_view.xml',
        'views/history_register_of_directors_view.xml',
        'views/history_register_of_managers_view.xml',
        'views/history_register_of_mortgages_view.xml',
        'views/history_register_of_nominee_directors_view.xml',
        'views/history_register_of_controllers_view.xml',
        'views/history_register_of_secretaries_view.xml',
        'views/history_register_of_transfer_view.xml',
    ],
}
