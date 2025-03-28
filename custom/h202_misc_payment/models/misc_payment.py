# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class misc_payment(models.Model):
    _name = 'misc.payment'

    @api.model
    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('name', '=', 'Miscellaneous Operations')])
        return journal.id

    name = fields.Char(readonly=True, copy=False, default="Draft Misc Payment")
    state = fields.Selection(
        [('draft', 'Draft'), ('posted', 'Validated'),('cancelled', 'Cancelled')], readonly=True, default='draft', copy=False, string="Status")
    payment_type = fields.Selection(
        [('outbound', 'Send Money'), ('inbound', 'Receive Money')],
        string='Payment Type', required=True, readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, default=_get_default_journal)
    account_id = fields.Many2one('account.account', 'Account', required=True, readonly=True, states={'draft': [('readonly', False)]})
    deposit_to_id = fields.Many2one('account.account', 'Deposit Account', required=True, readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Monetary(string='Amount', required=True, readonly=True, states={'draft': [('readonly', False)]},
                             tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    payment_date = fields.Date(string='Date', default=fields.Date.context_today, required=True, readonly=True,
                               states={'draft': [('readonly', False)]}, copy=False)
    communication = fields.Text(string="Communication", readonly=True, states={'draft': [('readonly', False)]})
    move_line_ids = fields.One2many('account.move.line', 'misc_payment_id', readonly=True, copy=False, ondelete='restrict')

    def action_draft(self):
        moves = self.mapped('move_line_ids.move_id')
        moves.filtered(lambda move: move.state == 'posted').button_draft()
        moves.with_context(force_delete=True).unlink()
        self.write({'state': 'draft'})

    def cancel(self):
        self.write({'state': 'cancelled'})

    def post(self):
        for rec in self:
            if rec.payment_type == 'inbound':
                name = rec.env['ir.sequence'].next_by_code('misc.payment.inbound')
            else:
                name = rec.env['ir.sequence'].next_by_code('misc.payment.outbound')
            rec.write({
                'name' : name,
                'state' : 'posted',
            })

            move_obj = self.env['account.move']
            line_ids = []
            line_ids.append((0, 0, {
                'account_id': rec.account_id.id,
                'debit': 0,
                'credit': rec.amount,
                'currency_id': rec.currency_id.id,
                'misc_payment_id' : rec.id
            }))

            line_ids.append((0, 0, {
                'account_id': rec.deposit_to_id.id,
                'debit': rec.amount,
                'currency_id': rec.currency_id.id,
                'credit': 0,
                'misc_payment_id': rec.id
            }))

            move_vals = {
                'journal_id': rec.journal_id.id,
                'date': fields.Datetime.now(),
                'ref': rec.name,
                'line_ids': line_ids,
                'type': 'entry',
            }

            move_id = move_obj.create(move_vals)
            move_id.action_post()

    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('misc_payment_id', 'in', self.ids)],
        }

    def unlink(self):
        if any(bool(rec.move_line_ids) for rec in self):
            raise UserError(_("You cannot delete a misc payment that is already posted."))
        return super(misc_payment, self).unlink()