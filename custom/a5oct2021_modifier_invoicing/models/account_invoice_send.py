# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.mail.wizard.mail_compose_message import _reopen
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang


class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'

    multi_print_partner_ids = fields.Many2many('res.partner', string='Recipients')
    check_same_partner = fields.Boolean(default=False)

    @api.model
    def default_get(self, fields):
        res = super(AccountInvoiceSend, self).default_get(fields)
        invoice_ids = res.get('invoice_ids', [])
        move_ids = self.env['account.move'].browse(invoice_ids)
        partner_ids = move_ids.mapped('partner_id').ids
        if invoice_ids and len(invoice_ids) > 0 and len(partner_ids) == 1:
            child_ids = self.env['res.partner'].search([('parent_id', 'in', move_ids.mapped('partner_id').ids),('email', '!=', False)])
            if child_ids:
                partner_ids += child_ids.ids

            res.update({
                'check_same_partner' : True,
                'multi_print_partner_ids' : partner_ids,
            })
        return res

    def send_and_print_action(self):
        if self.composition_mode == 'mass_mail' and self.template_id and self.multi_print_partner_ids:
            self.partner_ids = self.multi_print_partner_ids
        res = super(AccountInvoiceSend, self).send_and_print_action()
        return res