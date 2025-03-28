# -*- coding: utf-8 -*-

import json
from lxml import etree
from odoo import models, fields, api
from datetime import datetime, timedelta

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class daa_case(models.Model):
    _inherit = 'daa.case'

    commission_ids = fields.One2many('daa.case.commission', 'case_id', 'Commissions')

    visitation_ids = fields.One2many('mail.activity', 'case_id', compute='_compute_visitation_fees', inverse='_set_events', store=False, string='Visitation Fees')
    misc_ids = fields.One2many('mail.activity', 'case_id', compute='_compute_misc_fees', inverse='_set_events', store=False, string='Misc Fees')
    sub_fees_ids = fields.One2many('daa.sub.fees', 'case_id', string='Sub Fees')

    def compute_sub_fees(self):
        self.sub_fees_ids.unlink()
        if self.agreement_id:
            check = True
            start_date = self.agreement_id.contract_date
            last_date = self.agreement_id.end_date
            while check:
                to_compute = self.agreement_id.term_id.compute(self.agreement_id.sub_fees, start_date, currency=self.env.company.currency_id)
                if to_compute:
                    end_date = datetime.strptime(to_compute[0][0], DEFAULT_SERVER_DATE_FORMAT).date()
                    if end_date <= last_date:
                        self.sub_fees_ids += self.sub_fees_ids.new({
                            'sub_fees_amount' : to_compute[0][1],
                            'start_date' : start_date,
                            'end_date' : end_date,
                            'saleperson_id' : self.agreement_id.saleperson_id.id,
                            'sub_fee_comm' : to_compute[0][1] * 20 / 100,
                        })
                        start_date = end_date  + timedelta(days=1)
                    else:
                        check = False
            pass

    def _compute_visitation_fees(self):
        for case in self:
            case.visitation_ids = self.env['mail.activity'].search([
                ('debtor_id', '=', case.debtor_id.id),
                '|',
                ('status_id', '=', False),
                ('status_id.name', '!=', 'CLOSED'),
            ])

    def _compute_misc_fees(self):
        for case in self:
            case.misc_ids = self.env['mail.activity'].search([
                ('debtor_id', '=', case.debtor_id.id),
                '|',
                ('status_id', '=', False),
                ('status_id.name', '!=', 'CLOSED'),
            ])

    def _set_events(self):
        for record in self:
            pass

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        ret_val = super(daa_case, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        hide_commission = self.env.user.hide_commission
        if hide_commission:
            doc = etree.XML(ret_val['arch'])

            for node in doc.xpath("//page[@name='commission']"):
                node.set("invisible", "1")
                modifiers = json.loads(node.get("modifiers") or '{}')
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//page[@name='visitation_fee']"):
                node.set("invisible", "1")
                modifiers = json.loads(node.get("modifiers") or '{}')
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))

            for node in doc.xpath("//page[@name='misc_fee']"):
                node.set("invisible", "1")
                modifiers = json.loads(node.get("modifiers") or '{}')
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))

            ret_val['arch'] = etree.tostring(doc, encoding='unicode')

        return ret_val