# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

{
    'name': 'Dynamic Print Cheque - Check writing',
    'version': '13.0.1.0',
    'sequence':1,
    'category': 'Generic Modules/Accounting',
    'description': """
         App will  configure and print cheque/check Dynamically for any bank with different Cheque format.""",
    'author': 'DevIntelle Consulting Service Pvt.Ltd', 
    'website': 'http://www.devintellecs.com',
        'summary':'Dynamic Cheque report | Print Bank check  ',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/print_cheque_wizard_views.xml',
        'views/report_print_cheque.xml',
        'views/report_menu.xml',
        'views/cheque_setting_view.xml',
        'views/account_vocher_view.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price':35.0,
    'currency':'EUR',
    'live_test_url':'https://youtu.be/usddBBEk1Tg',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
