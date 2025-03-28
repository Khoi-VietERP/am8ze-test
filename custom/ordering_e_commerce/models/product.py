# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.tools.float_utils import float_round


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    show_in_ordering = fields.Boolean('Show in ordering')
    remarks = fields.Text('Remarks')
    ordering_sequence = fields.Integer('Ordering Sequence', default=10)
    product_pricelist_remark_ids = fields.One2many('product.pricelist.remark', 'product_tmp_id')

    @api.model
    def get_remarks(self, pricelist):
        product_pricelist_remark_ids = self.product_pricelist_remark_ids.filtered(lambda remark: remark.pricelist_id.id == pricelist.id)
        if product_pricelist_remark_ids:
            return product_pricelist_remark_ids[0].name
        else:
            return ""

class ProductProduct(models.Model):
    _inherit = 'product.product'

    show_in_ordering = fields.Boolean('Show in ordering', related="product_tmpl_id.show_in_ordering")
    remarks = fields.Text('Remarks', related="product_tmpl_id.remarks")
    ordering_sequence = fields.Integer('Ordering Sequence', related="product_tmpl_id.ordering_sequence")

    @api.model
    def check_qty_available(self,product_id,qty):
        product_id = self.sudo().search([('id', '=', product_id)])
        qty_return = qty
        if product_id:
            if product_id.qty_available < qty:
                qty_return = product_id.qty_available

        return qty_return

class ProductCategory(models.Model):
    _inherit = 'product.category'

    ordering_sequence = fields.Integer('Sequence', default=10)

class product_pricelist_remark(models.Model):
    _name = 'product.pricelist.remark'

    name = fields.Char(string="Remarks")
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    product_tmp_id = fields.Many2one('product.template')
