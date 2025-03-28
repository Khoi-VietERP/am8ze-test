# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    peppol_id = fields.Many2one('peppol.participant', 'Peppol ID', copy=False)
    peppol_reference = fields.Char('Peppol Reference')

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

    # def cron_partner_get_peppol_id(self):
    #     partner_ids = self.env['res.partner'].search([('peppol_id', '=', False),('l10n_sg_unique_entity_number', '!=', False)])
    #     for partner_id in partner_ids:
    #         peppol_ids = self.env['peppol.participant'].search([('name', 'ilike', partner_id.l10n_sg_unique_entity_number)])
    #         if len(peppol_ids) == 1:
    #             partner_id.peppol_id = peppol_ids
    #
    #     company_ids = self.env['res.company'].search([('peppol_id', '=', False),('l10n_sg_unique_entity_number', '!=', False)])
    #     for company_id in company_ids:
    #         peppol_ids = self.env['peppol.participant'].search([('name', 'ilike', company_id.l10n_sg_unique_entity_number)])
    #         if len(peppol_ids) == 1:
    #             company_id.peppol_id = peppol_ids

    def cron_partner_get_peppol_id(self):
        query = """SELECT rp.id as partner_id, pp.id as peppol_id
            FROM res_partner as rp 
            RIGHT JOIN peppol_participant as pp ON rp.l10n_sg_unique_entity_number = pp.name
            WHERE rp.l10n_sg_unique_entity_number IS NOT NULL"""
        self._cr.execute(query)
        res = self._cr.fetchall()
        for r in res:
            partner_id = self.env['res.partner'].browse(r[0])
            partner_id.write({
                'peppol_id': r[1]
            })

        company_ids = self.env['res.company'].search(
            [('peppol_id', '=', False), ('l10n_sg_unique_entity_number', '!=', False)])
        for company_id in company_ids:
            peppol_ids = self.env['peppol.participant'].search(
                [('name', 'ilike', company_id.l10n_sg_unique_entity_number)])
            if len(peppol_ids) == 1:
                company_id.peppol_id = peppol_ids
