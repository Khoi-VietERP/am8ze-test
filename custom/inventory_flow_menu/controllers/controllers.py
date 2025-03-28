# -*- coding: utf-8 -*-
# from odoo import http


# class InventoryFlowMenu(http.Controller):
#     @http.route('/inventory_flow_menu/inventory_flow_menu/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inventory_flow_menu/inventory_flow_menu/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inventory_flow_menu.listing', {
#             'root': '/inventory_flow_menu/inventory_flow_menu',
#             'objects': http.request.env['inventory_flow_menu.inventory_flow_menu'].search([]),
#         })

#     @http.route('/inventory_flow_menu/inventory_flow_menu/objects/<model("inventory_flow_menu.inventory_flow_menu"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inventory_flow_menu.object', {
#             'object': obj
#         })
