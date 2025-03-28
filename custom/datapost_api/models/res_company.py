# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    peppol_id = fields.Many2one('peppol.participant', 'Peppol ID', copy=False)
    contact_person = fields.Char("Contact Person")

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

    @api.model
    def register_send_email(self):
        return {
            'name': _("Register Peppol ID"),
            'res_model': 'company.register.popup',
            'view_mode': 'form',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'company_id': self.id,
            },
        }


class CompanyRegisterPopup(models.TransientModel):
    _name = 'company.register.popup'

    def company_register(self):
        company_id = self._context.get('company_id', False)
        if company_id:
            template = self.env.ref('datapost_api.company_register_email_template')
            if template:
                template.send_mail(company_id, force_send=True)

        return {
            'name': _("Notification"),
            'res_model': 'company.register.popup',
            'view_mode': 'form',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'company_id': False,
            },
        }
