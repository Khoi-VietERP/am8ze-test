# -*- coding: utf-8 -*-
{
    'name': "report_template_manual_payment_voucher",

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
        'base',
        'report_template_manual',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/voucher_payment_custom_template.xml',
    ],

}
