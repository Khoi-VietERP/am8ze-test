# Copyright 2020-2021 Openindustry.it SAS
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Stock 3D View',
    'version': '13.0.8.0.0',
    'license': 'OPL-1',
    'summary': """
        Stock 3D View enable to view pan and zoom multi warehouse locations in a 3d space
    """,
    'description': """
        Stock 3D View Multi Warehouse
    """,
    'author': 'Andrea Piovesana, Loris Tissino, Davide Corio, Matteo Boscolo',
    'support': 'andrea.m.piovesana@gmail.com',
    'website': 'https://openindustry.it',
    'category': 'Warehouse',
    'depends': [
        'stock_3dbase',
    ],
    'data': [
        'views/assets.xml',
        'views/stock_view.xml',
    ],
    'qweb': [
        'static/src/xml/templates.xml',
    ],
    'images': [
        'images/stock_3dview.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 150.00,
    'currency': 'EUR',
}
