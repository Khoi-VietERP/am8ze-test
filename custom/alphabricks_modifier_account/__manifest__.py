# -*- coding: utf-8 -*-
{
    'name': "alphabricks_modifier_account",

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
        'account',
        'snailmail_account',
        'mass_payments_for_multiple_vendors_customers',
        'modifier_gl_account_dynamic_reports',
        'paynow_qr_code',
        'sr_manual_currency_exchange_rate',
        'modifier_payments_for_multiple_vendors_customers',
        'a5oct2021_modifier_invoicing',
        'alphabricks_company_no_gst',
    ],

    'qweb': [
        "static/src/xml/account_payment.xml",
        "static/src/xml/tax_group.xml",
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/data.xml',
        'views/account_invoice_send_view.xml',
        'views/account_payment_method_view.xml',
        'views/chart_of_accounts_view.xml',
        'views/invoice_view.xml',
        'views/multiple_register_payments_view.xml',
        'views/res_config_settings_view.xml',
        'views/payment_popup_view.xml',
        'views/account_payment_view.xml',
        'data/data_account_type.xml',
        'views/account_report_setting.xml',

    ],
}
