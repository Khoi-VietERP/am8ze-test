# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import base64
import json
import webbrowser


class iras_api_submit(models.Model):
    _name = 'iras.api.submit'
    _description = 'IRAS API Submit'

    name = fields.Char(string="Sequence", default="New", readonly=1, copy=False)
    api_type = fields.Selection([
        ('submission_emp_income', 'Submission of Employment Income Records'),
        ('submission_gst', 'Submission of GST Returns'),
    ], default='submission_emp_income', required=1)
    file = fields.Binary(attachment=False)
    filename = fields.Char(string="Filename")
    file_type = fields.Selection([
        ('a8bInput', 'a8bInput'),
        ('a8aInput', 'a8aInput'),
        ('ir8sInput', 'ir8sInput'),
        ('ir8aInput', 'ir8aInput'),
    ], default='a8bInput')
    gst_file_type = fields.Selection([
        ('F5', 'F5'),
        ('F7', 'F7'),
        ('F8', 'F8'),
    ], default='F5')
    file_type_sub = fields.Char(compute='get_file_type', string='File Type')
    note = fields.Text(string="Note")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('error', 'Error'),
    ], default='draft')

    def get_file_type(self):
        for rec in self:
            if rec.api_type == 'submission_emp_income':
                rec.file_type_sub = rec.file_type
            elif rec.api_type == 'submission_gst':
                rec.file_type_sub = rec.gst_file_type

    def get_scope(self):
        scope = ''
        if self.api_type == 'submission_emp_income':
            scope = "EmpIncomeSub"
        elif self.api_type == 'submission_gst':
            if self.gst_file_type in ('F5', 'F8'):
                scope = 'GSTF5F8SubCP'
            elif self.gst_file_type == 'F7':
                scope = 'GSTF7SubCP'
        return scope

    def send_submit(self):
        iras_api_config_id = self.env.ref('odoo_integrate_iras_api.iras_api_config_data')
        scope = self.get_scope()
        return iras_api_config_id.get_authorisation_code(self.name, scope)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].sudo().next_by_code('iras.api.submit')
        return super(iras_api_submit, self).create(vals)

    def copy(self, default=None):
        res = super(iras_api_submit, self).copy(default=default)
        if not res.name or res.name == 'New':
            res.name = self.env['ir.sequence'].sudo().next_by_code('iras.api.submit')
        return res