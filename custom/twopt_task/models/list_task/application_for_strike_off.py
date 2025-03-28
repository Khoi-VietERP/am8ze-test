# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class application_for_strike_off(models.Model):
    _name = "application.for.strike.off"

    uen = fields.Char('UEN')
    entity_id = fields.Many2one('corp.entity', 'Entity', compute='get_entity', store=True)
    entity_name = fields.Char(string="Entity Name", compute='get_entity', store=True)
    name = fields.Char('Name', compute='get_entity', store=True)
    lable_All_Majority = fields.Char(compute='_get_data_entity')
    line_ids = fields.One2many('application.for.strike.off.line', 'parent_id')
    reason_for_application = fields.Many2one('reason.for.application', string="Reason for Application")
    check_show_ceased_date = fields.Boolean(compute="get_show_ceased_date")
    ceased_date = fields.Date(string="Ceased Date")
    last_transaction_date = fields.Date(string="Last Transaction Date")
    bank_account_close_date = fields.Date(string="Bank Account Close Date")

    check_box_1 = fields.Boolean(string="The company has no outstanding tax liabilities owing to the inland Revenue Authority"
                                        "of Singapore (IRAS) and is not indebted to any other Government Agency")
    check_box_2 = fields.Boolean(string="The company is not a party to any ongoing or pending proceedings (whether civil or criminal)"
                                        "before a court, whether in Singapore or elsewhere")
    check_box_3 = fields.Boolean(string="The company is not subject to any ongoing or pending regulatory action or disciplinary proceeding")
    check_box_4 = fields.Boolean(string="The company has no assets or contingent assets and no liabilities or contingent liabilities")

    @api.depends('reason_for_application')
    def get_show_ceased_date(self):
        reason_for_application_1 = self.env.ref('twopt_task.reason_for_application_1')
        if self.reason_for_application and self.reason_for_application == reason_for_application_1:
            self.check_show_ceased_date = True
        else:
            self.check_show_ceased_date = False

    @api.depends('entity_id')
    def _get_data_entity(self):
        for rec in self:
            if rec.entity_id:
                secretary = self.env.ref('corp_sec_entity.position_secretary').id
                secretary_id = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', secretary)
                ], limit=1)
                rec.lable_All_Majority = "All/Majority of the directors authorise me, %s, " \
                                         "to submit this application for striking off on behalf of the company." % (secretary_id.name or '')

                director = self.env.ref('corp_sec_entity.position_director').id
                director_ids = self.env['contact.associations'].search([
                    ('entity_id', '=', self.entity_id.id),
                    ('position_detail_id', '=', director)
                ])
                line_data = [(5, 0, 0)]
                for director_id in director_ids:
                    line_data.append((0, 0, {'name': director_id.name, 'identification_no': director_id.nric}))

                rec.line_ids = line_data
            else:
                rec.lable_All_Majority = ''
                rec.line_ids = False

    @api.depends('uen')
    def get_entity(self):
        for rec in self:
            if rec.uen:
                entity_id = self.env['corp.entity'].search([('uen', '=', rec.uen)])
                if entity_id:
                    rec.entity_name = entity_id.name
                    rec.name = entity_id.name

                else:
                    rec.entity_name = 'This Entity does not exist in system'
                    rec.name = ''

                rec.entity_id = entity_id
            else:
                rec.entity_id = False
                rec.entity_name = ''
                rec.name = ''

    @api.model
    def create(self, vals):
        res = super(application_for_strike_off, self).create(vals)
        self.env['project.task'].create({
            'name': 'Application for strike off',
            'application_for_strike_off_id': res.id,
            'task_type': 'application-for-strike-off',
            'entity_id': res.entity_id.id,
        })
        return res

class application_for_strike_off_line(models.Model):
    _name = 'application.for.strike.off.line'

    name = fields.Char(string="Name")
    identification_no = fields.Char(string="Identification No.")
    parent_id = fields.Many2one('application.for.strike.off')