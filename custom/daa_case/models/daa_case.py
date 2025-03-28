# -*- coding: utf-8 -*-

import json
from lxml import etree
from odoo import models, fields, api
from datetime import datetime

class daa_case(models.Model):
    _name = 'daa.case'
    _description = 'Case'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # partner_id = fields.Many2one('res.partner', required=True)

    name = fields.Char('Name')
    stage_id = fields.Many2one('daa.case_stage', 'Case Status')
    transfer_date = fields.Date('Transfer Date')

    client_id = fields.Many2one('res.partner', string='Client', required=True)
    debtor_id = fields.Many2one('res.partner', domain=[('is_debtor', '=', True)], string='Debtor')
    agreement_id = fields.Many2one('daa.agreement', 'Agreement')
    ref = fields.Char('Case Ref')

    guarantor_1 = fields.Many2one('res.partner', domain=[('is_guarantor', '=', True)], string='Guarantor 1')
    guarantor_2 = fields.Many2one('res.partner', domain=[('is_guarantor', '=', True)], string='Guarantor 2')
    guarantor_3 = fields.Many2one('res.partner', domain=[('is_guarantor', '=', True)], string='Guarantor 3')
    guarantor_4 = fields.Many2one('res.partner', domain=[('is_guarantor', '=', True)], string='Guarantor 4')
    guarantor_5 = fields.Many2one('res.partner', domain=[('is_guarantor', '=', True)], string='Guarantor 5')
    line_officer_1 = fields.Many2one('hr.employee', 'Line Officer 1')
    line_officer_2 = fields.Many2one('hr.employee', 'Line Officer 2')
    credit_officer_1 = fields.Many2one('hr.employee', 'Credit Officer 1')
    credit_officer_2 = fields.Many2one('hr.employee', 'Credit Officer 2')

    debt_amount = fields.Monetary('Debt Amount', compute='_compute_amount', currency_field='currency_id')
    total_amount = fields.Monetary('Credit Adjustment', compute='_compute_amount', currency_field='currency_id')
    assigned_amount = fields.Monetary('Received Amount', compute='_compute_amount', currency_field='currency_id')
    # collected_amount = fields.Monetary('Collected Amount', currency_field='currency_id')
    balance_amount = fields.Monetary('Balance', compute='_compute_amount', currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.company.currency_id)
    is_validation = fields.Boolean('Validation', default=False)
    # user_id = fields.Many2one('res.users', 'Assigned Officer')
    # employee_id = fields.Many2one('hr.employee', 'Assigned Officer')
    document_ids = fields.One2many('document.document', 'case_id', 'Documents')

    charge_ids = fields.One2many('daa.case.charge', 'case_id', 'Charge Details')
    payment_ids = fields.One2many('daa.case.payment', 'case_id', 'Payment History')
    contact_ids = fields.One2many('res.partner', 'case_id', compute='_compute_contacts', inverse='_set_contacts', string='Contacts')

    def _set_contacts(self):
        for record in self:
            for contact in record.contact_ids:
                pass

    def _compute_contacts(self):
        for record in self:
            contact_ids = self.env['res.partner'].search([
                ('case_id', '=', record.id),
            ])
            if record.debtor_id:
                contact_ids += record.debtor_id
            if record.guarantor_1:
                contact_ids += record.guarantor_1
            if record.guarantor_2:
                contact_ids += record.guarantor_2
            if record.guarantor_3:
                contact_ids += record.guarantor_3
            if record.guarantor_4:
                contact_ids += record.guarantor_4
            if record.guarantor_5:
                contact_ids += record.guarantor_5
            record.contact_ids = contact_ids

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        ret_val = super(daa_case, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        hide_agreement = self.env.user.hide_agreement
        if hide_agreement:
            doc = etree.XML(ret_val['arch'])

            for node in doc.xpath("//field[@name='agreement_id']"):
                node.set("invisible", "1")
                modifiers = json.loads(node.get("modifiers") or '{}')
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))

            ret_val['arch'] = etree.tostring(doc, encoding='unicode')

        return ret_val


    @api.onchange('client_id')
    def _onchange_client_id(self):
        for record in self:
            if record.client_id and len(record.client_id.agreement_ids) > 0:
                record.agreement_id = record.client_id.agreement_ids[0]

    @api.depends('charge_ids.assign_amount', 'charge_ids.adjust_amount', 'charge_ids.total_amount', 'charge_ids.balance_amount')
    def _compute_amount(self):
        for record in self:
            debt_amount = total_amount = assigned_amount = balance_amount = 0

            for charge in record.charge_ids:
                debt_amount += charge.assign_amount
                total_amount += charge.adjust_amount
                assigned_amount += charge.total_amount
                balance_amount += charge.balance_amount

            record.debt_amount = debt_amount
            record.total_amount = total_amount
            record.assigned_amount = assigned_amount
            record.balance_amount = balance_amount

    def print_dunning_letter(self):
        data = {
            'name': self.stage_id.name,
            'company_type': self.client_id.company_type,
            'date': self.transfer_date and self.transfer_date.strftime('%d/%m/%Y'),
            'case_ref': self.ref or '',
            'balance': self.balance_amount,
            'blk_no': self.client_id.address_ids.blk_no,
            'street': self.client_id.address_ids.street_name,
            'unit': self.client_id.address_ids.unit_level,
            'building_name': self.client_id.address_ids.building_name,
            'postal_code': self.client_id.address_ids.postal_code,
        }
        report_name = 'daa_case.dunning_letter_report'
        return self.env.ref(report_name).report_action(self, data=data)

    def name_get(self):
        self.browse(self.ids).read([])
        return [(case.id, '%s' %(case.id,)) for case in self]