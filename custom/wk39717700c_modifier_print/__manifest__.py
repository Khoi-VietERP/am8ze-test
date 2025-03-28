# -*- coding: utf-8 -*-
{
    'name': "wk39717700c_modifier_print",

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
        'purchase',
        'wk39717700c_modifier_partner',
        'sale',
        'account',
        'stock',
        'wk39717700c_sale_foc',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/template.xml',
        'views/ageing_summary_report_view.xml',
        'views/salesman_invoice_detail_view.xml',
        'views/supplier_outstanding_view.xml',
        'reports/purchase_invoice_report.xml',
        'reports/purchase_payment_detail_report.xml',
        'reports/purchase_order_report.xml',
        'reports/sale_invoice_report.xml',
        'reports/delivery_order_report.xml',
        'reports/credit_note_report.xml',
        'reports/receipt_report.xml',
        'reports/statement_of_account_report.xml',
        'reports/ageing_summary_report.xml',
        'reports/salesman_invoice_detail_report.xml',
        'reports/supplier_outstanding_report.xml',
        'reports/statement_account_by_date_view.xml',
        'reports/layouts.xml',
        'views/res_config_settings_view.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}
