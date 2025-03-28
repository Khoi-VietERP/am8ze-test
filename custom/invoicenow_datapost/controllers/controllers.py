# -*- coding: utf-8 -*-
# from odoo import http


# class DaaDatapost(http.Controller):
#     @http.route('/daa_datapost/daa_datapost/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/daa_datapost/daa_datapost/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('daa_datapost.listing', {
#             'root': '/daa_datapost/daa_datapost',
#             'objects': http.request.env['daa_datapost.daa_datapost'].search([]),
#         })

#     @http.route('/daa_datapost/daa_datapost/objects/<model("daa_datapost.daa_datapost"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('daa_datapost.object', {
#             'object': obj
#         })
