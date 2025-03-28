# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quotation_prefix_id = fields.Many2one('ir.sequence', 'Quotation Prefix', domain="[('quotation_prefix', '=', True)]", required=0)

    def set_sale_field(self, field, value):
        key = "sale.old.%s" % field
        self.env['ir.config_parameter'].sudo().set_param(key, value)
        return True

    def get_sale_field(self, field):
        key = "sale.old.%s" % field
        return self.env['ir.config_parameter'].sudo().get_param(key)

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'quotation_prefix_id' in vals:
            for rec in self:
                self.set_sale_field('quotation_prefix_id', rec.quotation_prefix_id.id or False)
        return res

    @api.model
    def create(self, vals):
        quotation_prefix_id = vals.get('quotation_prefix_id', False)
        if quotation_prefix_id:
            order_name = self.env['ir.sequence'].browse(quotation_prefix_id).next_by_id()
            vals.update({
                'name' : order_name
            })
        res = super(SaleOrder, self).create(vals)
        self.set_sale_field('quotation_prefix_id', res.quotation_prefix_id.id or False)
        return res

    @api.model
    def default_get(self, default_fields):
        res = super(SaleOrder, self).default_get(default_fields)

        if self.get_sale_field('quotation_prefix_id'):
            res['quotation_prefix_id'] = int(self.get_sale_field('quotation_prefix_id'))

        return res
