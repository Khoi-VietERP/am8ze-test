#  -*- encoding: utf-8 -*-

{
    "name": "Top Modifier Account",
    "version": "13.0.1.0.0",
    "license": "LGPL-3",
    "depends": ['account','modifier_customer_vendor'],
    "author": "VietERP/Sang",
    "maintainer": "SVietERP/Sang",
    "category": "Accounting",
    "description": """
        Modifier Accounting View
    """,
    "data": [
        "views/account_move_view.xml",
        "views/account_payment_view.xml",
        "views/invoice_sequence_menu.xml",
    ],
    "installable": True,
    "auto_install": True,
}
