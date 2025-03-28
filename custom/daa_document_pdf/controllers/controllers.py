# -*- coding: utf-8 -*-
# from odoo import http


# class DaaDocumentPdf(http.Controller):
#     @http.route('/daa_document_pdf/daa_document_pdf/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/daa_document_pdf/daa_document_pdf/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('daa_document_pdf.listing', {
#             'root': '/daa_document_pdf/daa_document_pdf',
#             'objects': http.request.env['daa_document_pdf.daa_document_pdf'].search([]),
#         })

#     @http.route('/daa_document_pdf/daa_document_pdf/objects/<model("daa_document_pdf.daa_document_pdf"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('daa_document_pdf.object', {
#             'object': obj
#         })
