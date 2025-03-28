# -*- coding: utf-8 -*-

from odoo import models, fields, api


class recurring_invoice_template(models.Model):
    _name = 'recurring.invoice.template'

    invoice_id = fields.Many2one('account.move', string='Invoice', domain="[('type', '=', 'out_invoice')]")
    name = fields.Char('Name', related='invoice_id.name')
    partner_id = fields.Many2one('res.partner', string='Partner')
    first_date = fields.Datetime('Start Date', default=fields.Datetime.now)
    recurring_interval = fields.Integer('Recurring Interval', default=1)
    interval_type = fields.Selection([('days', 'Days'),
                                      ('weeks', 'Weeks'),
                                      ('months', 'Months')], default='days')
    recurring_number = fields.Integer('Number of Calls for Recurring', default=1)

    def create_recurring(self):
        recurring_invoice_id = self.env['recurring.invoice'].create({
            'name' : self.invoice_id.name,
            'partner_id' : self.partner_id.id,
            'total': self.invoice_id.amount_total,
            'due_date': self.invoice_id.invoice_date_due,
            'date_invoice': self.invoice_id.invoice_date,
            'first_date' : self.first_date,
            'recurring_interval' : self.recurring_interval,
            'interval_type' : self.interval_type,
            'recurring_number' : self.recurring_number,
            'recurring_invoice_template_id' : self.id,
        })
        recurring_invoice_id.confirm_recurring()

    def view_invoice(self):
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        form_view = [(self.env.ref('account.view_move_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.invoice_id.id
        return action

    @api.onchange('invoice_id')
    def onchange_partner(self):
        if self.invoice_id:
            self.partner_id = self.invoice_id.partner_id

