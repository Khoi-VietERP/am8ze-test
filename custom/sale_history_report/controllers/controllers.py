# -*- coding: utf-8 -*-
# from odoo import http


# class SaleHistoryReport(http.Controller):
#     @http.route('/sale_history_report/sale_history_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_history_report/sale_history_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_history_report.listing', {
#             'root': '/sale_history_report/sale_history_report',
#             'objects': http.request.env['sale_history_report.sale_history_report'].search([]),
#         })

#     @http.route('/sale_history_report/sale_history_report/objects/<model("sale_history_report.sale_history_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_history_report.object', {
#             'object': obj
#         })
