# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class corp_sec_entity(models.Model):
    _inherit = 'corp.entity'

    project_task_ids = fields.One2many('project.task', 'entity_id')

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if not self._context.get('search_not_is_entity', False):
            args.append(('not_is_entity', '=', False))
        return super(corp_sec_entity, self)._search(args, offset, limit, order, count=count,
                                               access_rights_uid=access_rights_uid)

    def print_client_dd_and_declaration_form(self):
        report_name = "Client DD and Declaration Form.doc"
        print_name = "twopt_task.client_dd_and_declaration_form"
        attachment_ids = self.env['ir.attachment'].search([
            ('res_model', '=', 'corp.entity'),
            ('res_id', '=', self.id),
            ('name', '=', report_name),
        ])
        if attachment_ids:
            attachment_ids.unlink()

        data = {}

        self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'corp.entity', self.id,
                                                               data)

        attachment_ids = self.env['ir.attachment'].search([
            ('res_model', '=', 'corp.entity'),
            ('res_id', '=', self.id),
            ('name', '=', report_name),
        ])

        attachments = []
        for attach in attachment_ids:
            attachments.append(attach.id)

        url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def print_notice_of_registrable_controller(self):
        report_name = "Notice of Registrable Controller.doc"
        print_name = "twopt_task.notice_of_registrable_controller"
        attachment_ids = self.env['ir.attachment'].search([
            ('res_model', '=', 'corp.entity'),
            ('res_id', '=', self.id),
            ('name', '=', report_name),
        ])
        if attachment_ids:
            attachment_ids.unlink()

        data = {}

        self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'corp.entity', self.id,
                                                               data)

        attachment_ids = self.env['ir.attachment'].search([
            ('res_model', '=', 'corp.entity'),
            ('res_id', '=', self.id),
            ('name', '=', report_name),
        ])

        attachments = []
        for attach in attachment_ids:
            attachments.append(attach.id)

        url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

    def print_risk_assessment_form(self):
        report_name = "Risk Assessment Form.doc"
        print_name = "twopt_task.risk_assessment_form"
        attachment_ids = self.env['ir.attachment'].search([
            ('res_model', '=', 'corp.entity'),
            ('res_id', '=', self.id),
            ('name', '=', report_name),
        ])
        if attachment_ids:
            attachment_ids.unlink()

        data = {}

        self.env['ir.actions.report'].create_attachment_report(report_name, print_name, 'corp.entity', self.id,
                                                               data)

        attachment_ids = self.env['ir.attachment'].search([
            ('res_model', '=', 'corp.entity'),
            ('res_id', '=', self.id),
            ('name', '=', report_name),
        ])

        attachments = []
        for attach in attachment_ids:
            attachments.append(attach.id)

        url = '/web/binary/download_multi_attachment?tab_id=%s' % attachments
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }