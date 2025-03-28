# -*- coding: utf-8 -*-
# from odoo import http


# class DaaField(http.Controller):
#     @http.route('/daa_field/daa_field/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/daa_field/daa_field/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('daa_field.listing', {
#             'root': '/daa_field/daa_field',
#             'objects': http.request.env['daa_field.daa_field'].search([]),
#         })

#     @http.route('/daa_field/daa_field/objects/<model("daa_field.daa_field"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('daa_field.object', {
#             'object': obj
#         })
