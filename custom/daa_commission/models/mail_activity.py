# -*- coding: utf-8 -*-

from odoo import models, fields, api

class mail_activity(models.Model):
    _inherit = 'mail.activity'

    def _get_default_visitation_fees(self):
        result = 0
        if self._context.get('agreement_id', False):
            agreement_id = self.env['daa.agreement'].browse(self._context.get('agreement_id', False))
            result = agreement_id.visitation_fee
        return result

    def _get_default_misc_fees(self):
        result = 0
        if self._context.get('agreement_id', False):
            agreement_id = self.env['daa.agreement'].browse(self._context.get('agreement_id', False))
            result = agreement_id.misc_fee
        return result

    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.company.currency_id)

    visitation_fees = fields.Monetary('Visitation Fees', default=_get_default_visitation_fees, currency_field='currency_id')
    visitation_company = fields.Float('Visitation Company (%)', default=1/3*100)
    visitation_company_amount = fields.Monetary('Visitation Company', currency_field='currency_id')
    visitation_collector = fields.Float('Visitation Collector (%)', default=2/3*100)
    visitation_collector_amount = fields.Monetary('Visitation Collector', currency_field='currency_id')

    misc_fees = fields.Monetary('Misc Fees', default=_get_default_misc_fees, currency_field='currency_id')
    misc_company = fields.Float('Misc Company (%)', default=60)
    misc_company_amount = fields.Monetary('Misc Company', currency_field='currency_id')
    misc_collector = fields.Float('Misc Collector (%)', default=40)
    misc_collector_amount = fields.Monetary('Misc Collector', currency_field='currency_id')

    @api.onchange('visitation_fees', 'visitation_company', 'visitation_collector')
    def onchange_visitation_fees(self):
        for record in self:
            record.visitation_company_amount = record.visitation_fees * record.visitation_company / 100
            record.visitation_collector_amount = record.visitation_fees * record.visitation_collector / 100

    @api.onchange('misc_fees', 'misc_company', 'misc_collector')
    def onchange_misc_fees(self):
        for record in self:
            record.misc_company_amount = record.misc_fees * record.misc_company / 100
            record.misc_collector_amount = record.misc_fees * record.misc_collector / 100