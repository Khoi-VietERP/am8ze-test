# -*- coding: utf-8 -*-

{
    'name': 'Pragtech Social Facebook',
    'category': 'Social',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'www.pragtech.co.in',
    'summary': '',
    'version': '13.0.1',
    'description': """""",
    'depends': ['pragtech_social'],
    'data': [
        'security/ir.model.access.csv',
        'data/facebook_social_media_data.xml',
        'views/facebook_assets.xml',
        'views/facebook_res_config_settings_views.xml',
        'views/post_view.xml',
        'views/facebook_comment_view.xml',
        'views/pragtech_social_stream_view.xml',
    ],
    'qweb': [
        "static/src/xml/comments.xml",
        "static/src/xml/posts.xml",
    ],
    'auto_install': False,
    'license': 'OPL-1',
}
