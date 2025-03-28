# -*- coding: utf-8 -*-
# from odoo import http


# class DaaAgreementContract(http.Controller):
#     @http.route('/daa_agreement_contract/daa_agreement_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/daa_agreement_contract/daa_agreement_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('daa_agreement_contract.listing', {
#             'root': '/daa_agreement_contract/daa_agreement_contract',
#             'objects': http.request.env['daa_agreement_contract.daa_agreement_contract'].search([]),
#         })

#     @http.route('/daa_agreement_contract/daa_agreement_contract/objects/<model("daa_agreement_contract.daa_agreement_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('daa_agreement_contract.object', {
#             'object': obj
#         })
