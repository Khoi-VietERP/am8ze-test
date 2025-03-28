from odoo import api, fields, models,_
from odoo.exceptions import UserError

class SaleOrderReturn(models.Model):
    _inherit = "sale.order.return"

    invoice_count = fields.Integer(string='Invoice Count', compute='_get_invoiced')

    def _get_invoiced(self):
        invoices = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        self.invoice_count = len(invoices)

    # def button_confirm(self):
    #     picking_type_id = self.env['stock.picking.type'].search(
    #         [('code', '=', 'incoming'),
    #          ('company_id', '=', self.company_id.id)], limit=1)
    #     if picking_type_id:
    #         res = self._prepare_picking(self, picking_type_id)
    #         new_picking_id = self.env['stock.picking'].create(res)
    #         self.knk_sale_order_id.knk_picking_ids = [(4, new_picking_id.id, 0)]
    #         self.knk_picking_ids = [(4, new_picking_id.id, 0)]
    #         for line in self.knk_sale_order_return_line_ids:
    #             move_vals = self._prepare_stock_moves(self, line, picking_type_id, new_picking_id)
    #             for move_val in move_vals:
    #                 self.env['stock.move'].create(move_val)._action_confirm()._action_assign()
    #         #     self.env.cr.commit()
    #         # self.process(new_picking_id)
    #         self.state = 'confirm'
    #         try:
    #             res = new_picking_id.button_validate()
    #             if res:
    #                 if res.get('res_model') == 'stock.immediate.transfer':
    #                     wizard = self.env['stock.immediate.transfer'].browse(
    #                         res.get('res_id'))
    #                     wizard.process()
    #                     return True
    #             return res
    #         except Exception:
    #             pass
    #     return True


    def action_view_invoice(self):
        invoices = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        self.ensure_one()

        action = {
            'res_model': 'account.move',
            'type': 'ir.actions.act_window'
        }

        action.update({
            'name': 'Credit Notes',
            'domain': [('id', 'in', invoices.ids)],
            'view_mode': 'tree,form'
        })
        return action

    def action_create_invoice(self):
        invoice_id = self.env['account.move'].with_env(self.env(user=self.env.uid)).create({
            'type': 'out_refund',
            'invoice_origin': self.name,
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Datetime.now(),
            'date': self.date_of_return,
            'invoice_date_due': fields.Datetime.now(),
        })

        invoice_line = []
        for line in self.knk_sale_order_return_line_ids:
            accounts = line.knk_product_id.product_tmpl_id.get_product_accounts()
            account_id = accounts['income']
            invoice_line.append((0, 0, {
                'product_id': line.knk_product_id.id,
                'quantity': line.knk_product_qty,
                'price_unit': line.price,
                'name': line.knk_product_id.display_name,
                'account_id': account_id.id,
            }))
        invoice_id.with_context(journal_id=1).write({'invoice_line_ids': invoice_line})

        action = {
            'name': _('Reverse Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }
        action.update({
            'view_mode': 'form',
            'res_id': invoice_id.id,
            'context': {'default_type': invoice_id.type},
        })
        return action
