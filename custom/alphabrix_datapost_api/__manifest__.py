# -*- coding: utf-8 -*-
{
    'name': "alphabrix_datapost_api",

    'summary': """
        alphabrix_datapost_api
    """,

    'description': """
        alphabricks_datapost_api
    """,

    'author': "VietERP / Sang",
    'website': "http://www.vietep.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'VietERP',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'l10n_sg',
        'sale',
        'purchase',
        'uom',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/datapost_api_view.xml',
        'views/datapost_document_view.xml',
        'views/datapost_response_view.xml',
        'views/datapost_received_view.xml',
        'views/datapost_received_batch_view.xml',
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
        'views/account_move_view.xml',
        'views/purchase_order_view.xml',
        'views/sale_order_view.xml',
        # 'views/peppol_participant_view.xml',
        'views/uom_uom_views.xml',
        'wizards/datapost_response_code_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
