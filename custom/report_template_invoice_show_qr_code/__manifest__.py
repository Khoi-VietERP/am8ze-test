# -*- coding: utf-8 -*-
{
    'name': "report_template_invoice_show_qr_code",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Sang",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'report_template_invoice',
        'paynow_qr_code'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/report_custom_template1.xml',
        'report/report_custom_template2.xml',
    ],
}
