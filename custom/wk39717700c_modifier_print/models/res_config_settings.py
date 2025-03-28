# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_invoice_note = fields.Text('Sale Invoice Print Note')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            sale_invoice_note=self.env['ir.config_parameter'].get_param('wk39717700c_modifier_print.sale_invoice_note')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        sale_invoice_note = 'FOC Goods are not refundable or exchangeable.\n' \
                            'Expired goods are not refundable or exchangeable.\n' \
                            'Damaged goods can only be exchangeable within 7 days from date of delivery.\n' \
                            'Interest will be charged at 2% per month on overdue accounts.'
        self.env['ir.config_parameter'].set_param('wk39717700c_modifier_print.sale_invoice_note', self.sale_invoice_note or sale_invoice_note)