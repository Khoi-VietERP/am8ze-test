# -*- coding: utf-8 -*-
{
    'name': "report_quotation_pdf_top1",

    'summary': """
        report_quotation_pdf_top1
    """,

    'description': """
        report_quotation_pdf_top1
    """,

    'author': "Am8ze / Sang",
    'website': "http://www.am8ze.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Am8ze',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'account',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_templates.xml',
        'views/res_company_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
