# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    peppol_id = fields.Many2one('peppol.participant', 'Peppol ID', copy=False)

    @api.onchange('l10n_sg_unique_entity_number')
    def _peppol_onchange_l10n_sg_unique_entity_number(self):
        result = {'domain': {'peppol_id': []}}

        if self.l10n_sg_unique_entity_number:
            domain = [('name', 'ilike', self.l10n_sg_unique_entity_number)]
            participant = self.env['peppol.participant'].search(domain)
            if len(participant) == 1:
                self.peppol_id = participant
            result['domain']['peppol_id'] = domain

        return result