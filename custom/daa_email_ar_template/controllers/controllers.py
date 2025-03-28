# -*- coding: utf-8 -*-
# from odoo import http


# class DaaEmailArTemplate(http.Controller):
#     @http.route('/daa_email_ar_template/daa_email_ar_template/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/daa_email_ar_template/daa_email_ar_template/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('daa_email_ar_template.listing', {
#             'root': '/daa_email_ar_template/daa_email_ar_template',
#             'objects': http.request.env['daa_email_ar_template.daa_email_ar_template'].search([]),
#         })

#     @http.route('/daa_email_ar_template/daa_email_ar_template/objects/<model("daa_email_ar_template.daa_email_ar_template"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('daa_email_ar_template.object', {
#             'object': obj
#         })
