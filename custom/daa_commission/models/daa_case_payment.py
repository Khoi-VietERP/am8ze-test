# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class daa_case_payment(models.Model):
    _inherit = 'daa.case.payment'

    @api.model
    def create(self, values):
        res = super(daa_case_payment, self).create(values)
        if res.case_id and res.case_id.agreement_id and res.case_id.agreement_id.saleperson_id:
            self.env['daa.case.commission'].create({
                'payment_id': res.id,
                'received_amount': res.received_amount,
                'date': res.received_date,
                'saleperson_id': res.case_id.agreement_id.saleperson_id.id,
                'lo_misc_fees': res.case_id.agreement_id.misc_fee,
                'co_misc_fees': res.case_id.agreement_id.misc_fee,
                'case_id' : res.case_id.id,
            })
        if res.case_id.agreement_id and res.case_id.agreement_id.saleperson2_id:
            self.env['daa.case.commission'].create({
                'payment_id': res.id,
                # 'received_amount': res.received_amount,
                'date': res.received_date,
                'saleperson_id': res.case_id.agreement_id.saleperson2_id.id,
                'lo_misc_fees': res.case_id.agreement_id.misc_fee,
                'co_misc_fees': res.case_id.agreement_id.misc_fee,
                'case_id': res.case_id.id,
            })
        return res