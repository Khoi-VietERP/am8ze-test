# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from lxml import etree
from odoo.exceptions import UserError


class sale_order_ihr(models.Model):
    _inherit = 'sale.order'
    _order = 'name desc, date_order desc, id desc'

    tax_status = fields.Selection([
        ('tax_inclusive', 'Tax Inclusive'),
        ('tax_exclusive', 'Tax Exclusive'),
        ('no_tax', 'No Tax'),
    ], string="Amount are", default='tax_exclusive', required=1, states={'cancel': [('readonly', True)], 'done': [('readonly', True)]})
    amount_untaxed_signed = fields.Monetary(string='Untaxed Amount Signed', store=True, readonly=True,
                                            compute='_amount_all', currency_field='company_currency_id')
    amount_tax_signed = fields.Monetary(string='Tax Signed', store=True, readonly=True,
                                        compute='_amount_all', currency_field='company_currency_id')
    amount_total_signed = fields.Monetary(string='Total Signed', store=True, readonly=True,
                                          compute='_amount_all', currency_field='company_currency_id')
    partner_invoice_id = fields.Many2one(domain="['|',('id', '=', partner_id),('parent_id', '=', partner_id)]")
    partner_shipping_id = fields.Many2one(domain="['|',('id', '=', partner_id),('parent_id', '=', partner_id)]")

    @api.depends('order_line.price_total','apply_manual_currency_exchange','manual_currency_exchange_rate')
    def _amount_all(self):
        super(sale_order_ihr, self)._amount_all()
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax

            if order.apply_manual_currency_exchange and order.manual_currency_exchange_rate:
                amount_untaxed_signed = amount_untaxed * order.manual_currency_exchange_rate
                amount_tax_signed = amount_tax * order.manual_currency_exchange_rate
            else:
                amount_untaxed_signed = order.currency_id._convert(amount_untaxed,
                                                                  order.company_id.currency_id, order.company_id,
                                                                  order.date_order, round=False)
                amount_tax_signed = order.currency_id._convert(amount_tax,
                                                              order.company_id.currency_id, order.company_id,
                                                              order.date_order, round=False)
            order.update({
                'amount_untaxed_signed': amount_untaxed_signed,
                'amount_tax_signed': amount_tax_signed,
                'amount_total_signed': amount_untaxed_signed + amount_tax_signed,
            })

    @api.onchange('tax_status')
    def onchange_tax_status(self):
        if self.tax_status:
            if self.tax_status == "no_tax":
                for line in self.order_line:
                    line.tax_id = False
                    line._compute_amount()
            else:
                for line in self.order_line:
                    line._compute_tax_id()
                    line._compute_amount()

    def _prepare_invoice(self):
        invoice_vals = super(sale_order_ihr, self)._prepare_invoice()
        invoice_vals.update({
            'tax_status' : self.tax_status
        })
        return invoice_vals

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        ret_val = super(sale_order_ihr, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        if view_type == 'form':
            doc = etree.XML(ret_val['arch'])

            for node in doc.xpath("//field[@name='amount_total_signed']"):
                node.set("string", "Total (%s)" % self.env.company.currency_id.name)
            # for node in doc.xpath("//field[@name='amount_untaxed_signed']"):
            #     node.set("string", "Untaxed Amount (%s)" % self.env.company.currency_id.name)
            # for node in doc.xpath("//field[@name='amount_tax_signed']"):
            #     node.set("string", "GST (%s)" % self.env.company.currency_id.name)
            ret_val['arch'] = etree.tostring(doc, encoding='unicode')
        return ret_val

    @api.model
    def action_validate_stock(self):
         return {
            'type': 'ir.actions.act_window',
            'name':  _("Validate Stock"),
            'res_model': 'confirm.validate.stock',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('alphabricks_modifier_sale.view_confirm_validate_stock_form').id,
            'target': 'new',
            'context': {
                'default_sale_order_ids': [(6, 0, self.ids)]
            }
        }

class sale_order_line_ihr(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        if self.order_id.tax_status == 'tax_inclusive':
            self = self.with_context(force_price_include=True)
        super(sale_order_line_ihr, self)._compute_amount()

class ConfirmValidateStockWizard(models.TransientModel):
    _name = 'confirm.validate.stock'

    sale_order_ids = fields.Many2many('sale.order')
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking_ids')

    @api.depends('sale_order_ids')
    def _compute_picking_ids(self):
        for record in self:
            sale_order_ids = record.sale_order_ids.ids
            pickings = self.env['stock.picking'].search([('sale_id', 'in', sale_order_ids), ('state', '!=', 'done'), ('state', '!=', 'cancel')])
            record.picking_ids = pickings

    def action_confirm(self):
        for picking_id in self.picking_ids:
            picking_id.action_assign()
            if picking_id.state == 'assigned':
                self.env['stock.immediate.transfer'].with_context(
                    default_type=False
                ).create({'pick_ids': [(4, picking_id.id)]}).process()
            else:
                raise UserError(_("Haven't enough stock available"))
