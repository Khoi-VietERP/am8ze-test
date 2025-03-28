# -*- coding: utf-8 -*-

from odoo import models, fields, api
try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

class ResPartner(models.Model):
    _inherit = 'res.partner'

    peppol_reference = fields.Char('Peppol Reference')

    def get_peppol_db_partner(self):
        self.ensure_one()
        name_peppol = company_name_peppol = ''
        domain = [('name', 'ilike', self.l10n_sg_unique_entity_number)]
        api_id = self.env['datapost.api'].search([], limit=1)
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(api_id.peppol_url))
        uid = common.authenticate(api_id.peppol_db_name, api_id.peppol_login, api_id.peppol_password, {})
        models = xmlrpclib.ServerProxy(api_id.peppol_url + '/xmlrpc/object')
        peppol_id = models.execute_kw(api_id.peppol_db_name, uid, api_id.peppol_password, 'peppol.participant',
                                      'search', [domain])
        if peppol_id:
            peppol_data = \
            models.execute_kw(api_id.peppol_db_name, uid, api_id.peppol_password, 'peppol.participant', 'read',
                              [[peppol_id[0]], ['name', 'company_name']])[0]
            name_peppol = peppol_data.get('name', '0195:SGTST199404610D')
            company_name_peppol = peppol_data.get('company_name', '')
        return name_peppol, company_name_peppol
