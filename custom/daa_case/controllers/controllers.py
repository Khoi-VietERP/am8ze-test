# -*- coding: utf-8 -*-
# from odoo import http


# class DaaCaseContract(http.Controller):
#     @http.route('/daa_case_contract/daa_case_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/daa_case_contract/daa_case_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('daa_case_contract.listing', {
#             'root': '/daa_case_contract/daa_case_contract',
#             'objects': http.request.env['daa_case_contract.daa_case_contract'].search([]),
#         })

#     @http.route('/daa_case_contract/daa_case_contract/objects/<model("daa_case_contract.daa_case_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('daa_case_contract.object', {
#             'object': obj
#         })
