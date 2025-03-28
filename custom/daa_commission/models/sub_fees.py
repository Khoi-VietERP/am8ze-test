# -*- coding: utf-8 -*-

from odoo import models, fields, api

class daa_sub_fees(models.Model):
    _name = 'daa.sub.fees'
    _description = 'Sub Fees'

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    sub_fees_amount = fields.Monetary('Sub Feed Amount', currency_field='currency_id')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    saleperson_id = fields.Many2one('hr.employee', 'Sales Person')
    sub_fee_comm = fields.Monetary('Sub Fee Comm', currency_field='currency_id')
    case_id = fields.Many2one('daa.case', 'Case')