# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class contact_associations(models.Model):
    _inherit = 'contact.associations'

    def create_entity_history(self):
        for res in self:
            if res.position_detail_id:
                position_detail_id = res.position_detail_id
                if position_detail_id == self.env.ref('corp_sec_entity.position_director'):
                    self.env['history.register.of.directors'].create({
                        'entity_id': res.entity_id.id,
                        'name': res.contact_id.name,
                        'title': position_detail_id.name,
                        'passport_no': res.nric,
                        'date_of_appointment': datetime.now(),
                        'date_of_resignation': datetime.now(),
                    })
                elif position_detail_id == self.env.ref('corp_sec_entity.position_secretary'):
                    self.env['history.register.of.secretaries'].create({
                        'entity_id': res.entity_id.id,
                        'name': res.contact_id.name,
                        'title': position_detail_id.name,
                        'date_of_appointment': datetime.now(),
                        'date_of_cessation': datetime.now(),
                    })
                elif position_detail_id == self.env.ref('corp_sec_entity.position_auditor_individual'):
                    self.env['register.of.auditors'].create({
                        'entity_id': res.entity_id.id,
                        'line_ids': [(0, 0, {
                            'no': 1,
                            'auditors': res.contact_id.name,
                            'date_of_appointment': datetime.now(),
                            'date_of_cessation': datetime.now(),
                        })],
                    })
                elif position_detail_id == self.env.ref('corp_sec_entity.position_nominee_trustee'):
                    self.env['history.register.of.nominee.directors'].create({
                        'entity_id': res.entity_id.id,
                        'name': res.contact_id.name,
                        'title': position_detail_id.name,
                        'passport_no': res.nric,
                        'date_of_appointment': datetime.now(),
                        'date_of_resignation': datetime.now(),
                    })
                elif position_detail_id == self.env.ref('corp_sec_entity.position_owner'):
                    self.env['history.register.of.beneficial'].create({
                        'entity_id': res.entity_id.id,
                        'line_ids': [(0, 0, {
                            'name_of_registered': res.contact_id.name,
                            'nric': res.nric,
                        })],
                    })
                elif position_detail_id == self.env.ref('corp_sec_entity.position_controller'):
                    self.env['history.register.of.controllers'].create({
                        'entity_id': res.entity_id.id,
                        'name': res.contact_id.name,
                        'title': position_detail_id.name,
                        'passport_no': res.nric,
                        'date_of_registration': datetime.now(),
                        'date_of_de_registration': datetime.now(),
                    })

    @api.model
    def create(self, vals):
        res = super(contact_associations, self).create(vals)
        res.create_entity_history()
        return res

    def write(self, vals):
        res = super(contact_associations, self).write(vals)
        if vals.get('position_detail_id', False):
            self.create_entity_history()
        return res