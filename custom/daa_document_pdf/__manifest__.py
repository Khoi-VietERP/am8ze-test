# -*- coding: utf-8 -*-
{
    'name': "daa_document_pdf",

    'summary': """
        daa_document_pdf
    """,

    'description': """
        daa_document_pdf
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
        'report_pdf_preview',
        'document_management',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets.xml',
        'views/document_document_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
