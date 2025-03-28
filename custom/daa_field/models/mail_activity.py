# -*- coding: utf-8 -*-

import json
from lxml import etree
from odoo import models, fields, api

class mail_activity(models.Model):
    _inherit = 'mail.activity'

    case_id = fields.Many2one('daa.case', 'Case ID', domain=[])
    client_id = fields.Many2one('res.partner', related='case_id.client_id', string='Client')
    debtor_id = fields.Many2one('res.partner', string='Debtor')
    # time_deadline = fields.Float('Time')

    # action_code_id = fields.Many2one('daa.case_stage', compute='_compute_case_status', store=True, inverse='_set_case_status', string='Action Code')
    action_code_id = fields.Many2one('mail.activity.status', 'Action Code')
    # case_stage_id = fields.Many2one('daa.case_stage', compute='_compute_case_status', store=True, inverse='_set_case_status', string='Remarks')
    case_stage_id = fields.Text(string='Remarks')
    internal_remarks = fields.Text('Internal Remarks')

    employee_id = fields.Many2one('hr.employee', 'Officer')
    # remarks = fields.Char('System Remarks')

    status_id = fields.Many2one('daa.case_stage', 'Case Status')
    # description_id = fields.Many2one('daa.case_stage', compute='_compute_case_status', inverse='_set_case_status', store=True, string='Case Description')
    # description_id = fields.Many2one('mail.activity.description', 'Case Description')
    description_id = fields.Char('Case Description')

    @api.model
    def remove_invalid_event(self):
        pass

    @api.onchange('debtor_id')
    def onchange_debtor_id(self):
        for record in self:
            if record.debtor_id and record.debtor_id.id:
                return {'domain': {'case_id': [('debtor_id', '=', record.debtor_id.id)]}}
        return {'domain': {'case_id': []}}

    @api.onchange('case_id')
    def _onchange_case_id(self):
        if self.case_id and self.case_id.id:
            self.res_id = self.case_id.id
            self.res_model_id = self.env.ref('daa_case.model_daa_case')

    @api.onchange('case_id', 'case_id.debtor_id')
    def _compute_debtor(self):
        for record in self:
            if record.case_id.debtor_id and record.case_id.debtor_id.id:
                record.debtor_id = record.case_id.debtor_id

    def _set_case_status(self):
        for record in self:
            pass

    def do_saving(self):
        if isinstance(self.id, models.NewId):
            values = self.copy_data()
            item = self.create(values)
            pass

    # @api.depends('case_id.stage_id')
    # def _compute_case_status(self):
    #     for record in self:
    #         if record.case_id.stage_id and record.case_id.stage_id.id:
                # if not record.action_code_id or not record.action_code_id.id:
                #     record.action_code_id = record.case_id.stage_id
                # if not record.case_stage_id or not record.case_stage_id.id:
                #     record.case_stage_id = record.case_id.stage_id
                # if not record.description_id or not record.description_id.id:
                #     record.description_id = record.case_id.stage_id

    def print_dunning_letter(self):
        result = self.case_id.print_dunning_letter()
        return result