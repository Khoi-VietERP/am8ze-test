# -*- coding: utf-8 -*-
{
    'name': "wk39717700c_modifier_report",

    'summary': """
        wk39717700c_modifier_report
    """,

    'description': """
        wk39717700c_modifier_report
    """,

    'author': "VietERP / Sang",
    'website': "http://www.vieterp.vn",
    'category': 'VietERP',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'alphabricks_pnl_report',
        'alphabricks_bs_report',
        'gst_f5',
        'sg_account_report',
        'h202102879_modifier_menu',
        'modifier_ar_ap_report',
        'wk39717700c_modifier_print',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/data.xml',
        'views/template.xml',
        'views/customer_product_listing_popup.xml',
        'views/customer_top_selling_popup.xml',
        'views/invoice_summary_popup.xml',
        'views/invoice_summary_product_popup.xml',
        'views/product_customer_listing_popup.xml',
        'views/product_top_selling_popup.xml',
        'views/product_batch_stock_popup.xml',
        'views/product_batch_stock_movement_popup.xml',
        'views/product_foc_popup.xml',
        'views/pnl_report_wizard.xml',
        'views/balance_sheet_report_wizard.xml',
        'reports/customer_product_listing.xml',
        'reports/customer_top_selling.xml',
        'reports/invoice_summary.xml',
        'reports/invoice_summary_product.xml',
        'reports/product_customer_listing.xml',
        'reports/product_top_selling.xml',
        'reports/product_batch_stock.xml',
        'reports/product_batch_stock_movement.xml',
        'reports/report_product_foc.xml',
        'views/account_report_menu.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
}
