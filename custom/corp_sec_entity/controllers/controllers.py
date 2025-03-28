# -*- coding: utf-8 -*-
# from odoo import http


# class CorpSecEntity(http.Controller):
#     @http.route('/corp_sec_entity/corp_sec_entity/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/corp_sec_entity/corp_sec_entity/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('corp_sec_entity.listing', {
#             'root': '/corp_sec_entity/corp_sec_entity',
#             'objects': http.request.env['corp_sec_entity.corp_sec_entity'].search([]),
#         })

#     @http.route('/corp_sec_entity/corp_sec_entity/objects/<model("corp_sec_entity.corp_sec_entity"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('corp_sec_entity.object', {
#             'object': obj
#         })
