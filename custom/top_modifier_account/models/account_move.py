# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    price_unit_vendor = fields.Float(string='Unit Price', readonly=False, digits=dp.get_precision('Vendor Price Unit'))

    @api.onchange("price_unit_vendor")
    def onchange_price_unit_vendor(self):
        self.price_unit = self.price_unit_vendor

    def write(self, vals):
        return super(AccountMoveLine, self).write(vals)

    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
        self.ensure_one()
        if not price_unit and self.price_unit_vendor:
            price_unit = self.price_unit_vendor
        return self._get_price_total_and_subtotal_model(
            price_unit=price_unit or self.price_unit,
            quantity=quantity or self.quantity,
            discount=discount or self.discount,
            currency=currency or self.currency_id,
            product=product or self.product_id,
            partner=partner or self.partner_id,
            taxes=taxes or self.tax_ids,
            move_type=move_type or self.move_id.type,
        )

    @api.onchange('product_id', 'quantity')
    def onchange_check_qty_available(self):
        if self.product_id and self.quantity and self._context.get('default_type', False) == 'out_invoice':
            if self.quantity > self.product_id.qty_available:
                raise ValidationError("Stock Not Enough.")



class account_move(models.Model):
    _inherit = 'account.move'

    manual_amount = fields.Float(string='Manual Total')

    # def action_invoice_register_payment(self):
    #     if self.manual_amount:
    #         return self.env['account.payment'] \
    #             .with_context(active_ids=self.ids, active_model='account.move', active_id=self.id,invoice_manual_amount = self.manual_amount,default_payment_difference_handling = 'reconcile') \
    #             .action_register_payment()
    #     else:
    #         return super(account_move, self).action_invoice_register_payment()
    #     return self.env['account.payment']\
    #         .with_context(active_ids=self.ids, active_model='account.move', active_id=self.id)\
    #         .action_register_payment()

    def create_picking_from_out_invoice(self):
        for rec in self:
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)

            picking_customer = self.env['stock.picking'].create({
                'location_id': warehouse.lot_stock_id.id,
                'location_dest_id': rec.partner_id.property_stock_customer.id,
                'partner_id': rec.partner_id.id,
                'picking_type_id': warehouse.out_type_id.id,
                'origin': rec.name,
            })

            for line in rec.invoice_line_ids:
                self.env['stock.move'].create({
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_uom_id.id,
                    'picking_id': picking_customer.id,
                    'location_id': warehouse.lot_stock_id.id,
                    'location_dest_id': rec.partner_id.property_stock_customer.id,
                    'procure_method': 'make_to_stock',
                    'origin': rec.name,
                    'state': 'draft',
                })

            picking_customer.action_confirm()
            picking_customer.action_assign()
            if picking_customer.state == 'assigned':
                self.env['stock.immediate.transfer'].create({'pick_ids': [(4, picking_customer.id)]}).process()

    def action_post(self):
        res = super(account_move, self).action_post()
        for rec in self:
            sale_id = False
            if rec.invoice_origin:
                sale_id = self.env['sale.order'].search([('name', '=', rec.invoice_origin)], limit=1)
                if sale_id:
                    pickings = sale_id.mapped('picking_ids')
                    for picking in pickings:
                        if picking.state == 'assigned':
                            self.env['stock.immediate.transfer'].create({'pick_ids': [(4, picking.id)]}).process()
            if not sale_id and rec.type == 'out_invoice':
                for line in rec.invoice_line_ids:
                    if line.quantity > line.product_id.qty_available:
                        raise ValidationError("Stock Not Enough.")
                rec.create_picking_from_out_invoice()
        return res


class product_product(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('default_type', False) == 'out_invoice':
            res = []
            if args is None:
                args = []
            product_ids = self.search(['|', ('name', operator, name),
                                     ('default_code', operator, name)] + args, limit=limit)
            for product_id in product_ids:
                res.append((product_id.id, '[%s] %s. On hand: %s' % (product_id.default_code, product_id.name, product_id.qty_available)))
            return res
        else:
            return super(product_product, self).name_search(name=name, args=args, operator=operator, limit=limit)