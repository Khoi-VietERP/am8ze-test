# -*- coding: utf-8 -*-

import json
from lxml import etree
from odoo import models, fields, api

class res_partner_inherit(models.Model):
    _inherit = 'res.partner'

    is_main_contact = fields.Boolean('Is Main Contact', default=False)
    is_bill_to = fields.Boolean('Bill to', default=False)
    is_email_ack = fields.Boolean('Email Ack', default=False)
    is_debtor = fields.Boolean('Is Debtor', default=False)
    is_guarantor = fields.Boolean('Is Guarantor', default=False)

    status_id = fields.Many2one('partner.status', 'Status')
    # uen = fields.Char('UEN')
    nric = fields.Char('NRIC')
    industry_code_id = fields.Many2one('industry.code', 'Industry')

    contact_type = fields.Char('Contact Type')
    client_id = fields.Many2one('res.partner', domain=[('is_debtor', '=', False),('company_type', '=', "'company'")], string='Client')
    # client_status_id = fields.Many2one('partner.status', related='client_id.status_id')
    remarks = fields.Text('Remarks')

    phone = fields.Char('Phone')
    blk_no = fields.Char('Blk/No')
    unit_level = fields.Char('Unit/Level', default='#')
    # postal_code = fields.Char('Postal Code')
    street_name = fields.Char('Street')
    building_name = fields.Char('Building Name')

    address_ids = fields.One2many('partner.contact_address', 'partner_id', 'Addresses')
    phone_ids = fields.One2many('partner.contact_phone', 'partner_id', 'Phones')
    case_ids = fields.One2many('daa.case', string='Case Details', compute='_compute_cases')
    agreement_ids = fields.One2many('daa.agreement', 'client_id', 'Agreements')

    total_agreement = fields.Integer('Total Agreement', compute='_compute_agreement')

    contact_type = fields.Selection(selection=[
        ('contact', 'Contact'),
        # ('invoice', 'Invoice Address'),
        # ('delivery', 'Delivery Address'),
        # ('other', 'Other Address'),
        # ("private", "Private Address"),
    ], string='Address Type', default='contact', help="Invoice & Delivery addresses are used in sales orders. Private addresses are only visible by authorized users.")

    agreement_start_date = fields.Date('Start Date', compute='_compute_agreement')
    agreement_end_date = fields.Date('End Date', compute='_compute_agreement')
    agreement_daa_commission = fields.Integer('Commission Rate (%)', compute='_compute_agreement')
    agreement_sub_fees = fields.Monetary('Sub Fees', currency_field='currency_id', compute='_compute_agreement')
    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.company.currency_id)


    def print_dunning_letter(self):
        data = {
            'name': self.case_ids.stage_id.name,
            'company_type': self.company_type,
            'date': self.case_ids.transfer_date and self.case_ids.transfer_date.strftime('%d/%m/%Y'),
            'case_ref': self.case_ids.ref,
            'balance': self.case_ids.balance_amount,
            'blk_no': self.blk_no,
            'street': self.street,
            'unit': self.unit_level,
            'building_name': self.building_name,
            'postal_code': self.zip,
        }
        report_name = 'daa_case.dunning_letter_report'
        return self.env.ref(report_name).report_action(self, data=data)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        ret_val = super(res_partner_inherit, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        hide_event_tab = self.env.user.hide_event_tab
        if hide_event_tab:
            doc = etree.XML(ret_val['arch'])

            for node in doc.xpath("//page[@name='event_detail']"):
                node.set("invisible", "1")
                modifiers = json.loads(node.get("modifiers") or '{}')
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))

            ret_val['arch'] = etree.tostring(doc, encoding='unicode')

        return ret_val

    # def _set_events(self):
    #     for record in self:
    #         for event in record.event_ids:
    #             event.do_saving()
    #
    # def _compute_events(self):
    #     for partner in self:
    #         partner.event_ids = self.env['mail.activity'].search([
    #             '|',
    #             ('status_id', '=', False),
    #             ('status_id.name', '!=', 'CLOSED'),
    #             '|', '|',
    #             ('case_id.client_id', '=', partner.id),
    #             ('case_id.debtor_id', '=', partner.id),
    #             ('case_id.debtor_id.client_id', '=', partner.id),
    #         ])

    def _compute_cases(self):
        for partner in self:
            partner.case_ids = self.env['daa.case'].search([
                '|', '|',
                ('client_id', '=', partner.id),
                ('debtor_id', '=', partner.id),
                ('debtor_id.client_id', '=', partner.id),
            ])

    def action_view_daa_agreement(self):
        self.ensure_one()
        action = self.env.ref('daa_agreement.action_agreements').read()[0]
        action['domain'] = [
            ('client_id', 'child_of', self.id),
        ]
        action['context'] = {'default_client_id': self.id}
        return action

    def _compute_agreement(self):
        for record in self:
            record.total_agreement = len(record.agreement_ids.ids)

            agreement_start_date = agreement_end_date = agreement_daa_commission = agreement_sub_fees = False
            for agreement in record.agreement_ids:
                agreement_start_date = agreement.contract_date
                agreement_end_date = agreement.end_date
                agreement_daa_commission = agreement.daa_commission
                agreement_sub_fees = agreement.sub_fees
            record.agreement_start_date = agreement_start_date
            record.agreement_end_date = agreement_end_date
            record.agreement_daa_commission = agreement_daa_commission
            record.agreement_sub_fees = agreement_sub_fees

    def _check_upper_case_address(self, values):
        field_names = [
            'blk_no',
            'unit_level',
            'street',
            'building_name',
            'city',
            'zip',
        ]
        for field_name in field_names:
            if field_name in values and values.get(field_name, False):
                values[field_name] = values.get(field_name, '').upper()
        return values

    def _clone_address(self):
        main_address_values = {
            'is_main_address': True,
            'partner_id': self.id,
            'blk_no': self.blk_no,
            'unit_level': self.unit_level,
            'street_name': self.street,
            'building_name': self.building_name,
            'postal_code': self.zip,
        }
        main_contacts = self.address_ids.filtered(lambda a: a.is_main_address)
        if main_contacts and len(main_contacts.ids) > 0:
            main_contacts.write(main_address_values)
        else:
            self.address_ids.create(main_address_values)

    def _clone_main_phone(self):
        main_phone_values = {
            'is_main_phone': True,
            'partner_id': self.id,
            'name': self.mobile,
            'client_id': self.client_id.id,
        }
        if self.mobile:
            main_phones = self.phone_ids.filtered(lambda a: a.is_main_phone)
            if main_phones and len(main_phones.ids) > 0:
                main_phones.write(main_phone_values)
            else:
                self.phone_ids.create(main_phone_values)

    def write(self, values):
        values = self._check_upper_case_address(values)
        result = super().write(values)
        for record in self:
            record._clone_address()
            record._clone_main_phone()
        return result

    @api.model
    def create(self, values):
        values = self._check_upper_case_address(values)
        record = super().create(values)
        record._clone_address()
        record._clone_main_phone()
        return record

