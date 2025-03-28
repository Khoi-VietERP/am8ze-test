# -*- coding: utf-8 -*-

from odoo import models, fields, api

class crm_lead(models.Model):
    _inherit = 'crm.lead'
    _order = "create_date desc"

    blk_no = fields.Char('Blk/No')
    unit_level = fields.Char('Unit/Level', default='#')
    building_name = fields.Char('Building Name')

    name = fields.Char('Opportunity', required=False, index=False, default='Prospects')
    l10n_sg_unique_entity_number = fields.Char(string='UEN')

    @api.model
    def create(self, values):
        record = super(crm_lead, self).create(values)
        if record.stage_id.is_auto_client:
            record.handle_partner_assignation(action='create')
        return record

    def write(self, values):
        result = super(crm_lead, self).write(values)
        for record in self:
            if record.stage_id.is_auto_client:
                record.handle_partner_assignation(action='create')
        return result

    def _create_lead_partner_data(self, name, is_company, parent_id=False):
        res = super(crm_lead, self)._create_lead_partner_data(name, is_company, parent_id)

        res.update({
            'blk_no': self.blk_no,
            'unit_level': self.unit_level,
            'building_name': self.building_name,
            'l10n_sg_unique_entity_number': self.l10n_sg_unique_entity_number,
        })

        return res