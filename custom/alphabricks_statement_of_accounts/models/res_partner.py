# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    def get_partner_address(self):
        if self:
            data_list = []
            if self.street:
                data_list.append(self.street)
            if self.street2:
                data_list.append(self.street2)
            if self.city:
                data_list.append(self.city)
            if self.zip:
                data_list.append(self.zip)
            if self.country_id:
                data_list.append(self.country_id.name)

            return ', '.join(data_list)
        else:
            return ''

    @api.depends('balance_invoice_ids')
    def compute_days(self):
        today = fields.date.today()
        for partner in self:
            partner.first_thirty_day = 0
            partner.thirty_sixty_days = 0
            partner.sixty_ninty_days = 0
            partner.ninty_plus_days = 0
            if partner.balance_invoice_ids:
                for line in partner.balance_invoice_ids:
                    invoice_date_due = line.invoice_date_due or line.invoice_date
                    diff = today - invoice_date_due
                    if diff.days <= 30 and diff.days > 0:
                        partner.first_thirty_day = partner.first_thirty_day + line.result
                    elif diff.days > 30 and diff.days <= 60:
                        partner.thirty_sixty_days = partner.thirty_sixty_days + line.result
                    elif diff.days > 60 and diff.days <= 90:
                        partner.sixty_ninty_days = partner.sixty_ninty_days + line.result
                    else:
                        if diff.days > 90:
                            partner.ninty_plus_days = partner.ninty_plus_days + line.result
        return

    def search(self, args, offset=0, limit=None, order=None, count=False):
        new_args = []
        for arg in args:
            if 'check_outstanding_customers' in arg:
                move_ids = self.env['account.move'].search([('type', '=', 'out_invoice'),('amount_residual', '!=', 0)])
                partner_ids = move_ids.mapped('partner_id').ids
                new_args.append(('id', 'in', partner_ids))
            else:
                new_args.append(arg)
        return super(res_partner_inherit, self).search(new_args, offset, limit, order, count)