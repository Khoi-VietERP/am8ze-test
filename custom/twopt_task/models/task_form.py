# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class corp_entity(models.Model):
    _inherit = "corp.entity"

    task_type = fields.Selection([
        ('application-for-new-company', 'Application for new Company Name')
    ], 'Task Type', copy=False)
    not_is_entity = fields.Boolean(default=False, copy=False)

    @api.constrains('uen')
    def _check_entity_uen(self):
        for rec in self:
            if rec.uen:
                uen = self.search([('uen', '=', rec.uen),('not_is_entity', '=', False)])
                if len(uen) > 1:
                    raise ValidationError(_('This UEN has been used'))

    @api.model
    def create(self, vals):
        res = super(corp_entity, self).create(vals)
        if res.not_is_entity:
            self.env['project.task'].create({
                'name': dict(self.fields_get(['task_type'])['task_type']['selection']).get(res.task_type, ''),
                'task_form_id': res.id,
                'task_type': 'application-for-new-company',
            })
        return res

