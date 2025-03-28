# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    contact_person = fields.Char("Contact Person")

    def get_peppol_db_company(self):
        self.ensure_one()
        name_peppol = company_name_peppol = ''
        domain = [('name', 'ilike', self.l10n_sg_unique_entity_number)]
        api_id = self.env['datapost.api'].search([], limit=1)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(api_id.peppol_url))
        uid = common.authenticate(api_id.peppol_db_name, api_id.peppol_login, api_id.peppol_password, {})
        models = xmlrpclib.ServerProxy(api_id.peppol_url + '/xmlrpc/object')
        peppol_id = models.execute_kw(api_id.peppol_db_name, uid, password, 'peppol.participant',
                                      'search', [domain])
        if peppol_id:
            peppol_data = models.execute_kw(api_id.peppol_db_name, uid, password, 'peppol.participant', 'read',
                                            [[peppol_id[0]], ['name', 'company_name']])[0]
            name_peppol = peppol_data.get('name', '')
            company_name_peppol = peppol_data.get('company_name', '')
        return name_peppol, company_name_peppol

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
            template = self.env.ref('alphabrix_datapost_api.company_register_email_template')
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
