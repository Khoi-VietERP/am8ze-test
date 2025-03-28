# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from datetime import datetime

class daa_case_commission(models.Model):
    _name = 'daa.case.commission'
    _description = 'Case Commission'

    # @api.model
    # def _get_default_field_collector_1(self):
    #     for record in self:
    #         activities = self.env['mail.activity'].search([
    #             ('debtor_id', '=', record.case_id.debtor_id),
    #             ('employee_id', '!=', False),
    #         ], limit=2)
    #         if len(activities) == 2:
    #             record.field_collector_2 = activities[1].employee_id
    #         if len(activities) >= 1:
    #             record.field_collector_1 = activities[0].employee_id

    def _get_default_misc_fees(self):
        result = 0
        if self._context.get('agreement_id', False):
            agreement_id = self.env['daa.agreement'].browse(self._context.get('agreement_id', False))
            result = agreement_id.misc_fee
        return result


    case_id = fields.Many2one('daa.case', required=True)
    debtor_id = fields.Many2one('res.partner', 'Debtor')

    payment_id = fields.Many2one('daa.case.payment')
    currency_id = fields.Many2one('res.currency', required=True, default=lambda self: self.env.company.currency_id)
    received_amount = fields.Monetary('Received Amount', currency_field='currency_id')
    received_amount_sub = fields.Char('Received Amount', compute='get_received_amount')
    date = fields.Date('Date')
    saleperson_id = fields.Many2one('hr.employee', 'Sales Person')
    sale_comm = fields.Monetary('Total Com', currency_field='currency_id')
    line_officers_id = fields.Many2one('hr.employee', 'LO')
    lo_comm = fields.Monetary('Total Comm', currency_field='currency_id')
    lo_misc_fees = fields.Monetary('Total Misc', default=_get_default_misc_fees, currency_field='currency_id')
    visitation = fields.Char('Total Visitation')
    credit_officer_id = fields.Many2one('hr.employee', 'CO')
    co_comm = fields.Monetary('Total Comm', currency_field='currency_id')
    co_misc_fees = fields.Monetary('Total Misc', default=_get_default_misc_fees, currency_field='currency_id')


    field_collector_1 = fields.Many2one('hr.employee', 'Field Collector 1')
    field_collector_2 = fields.Many2one('hr.employee', 'Field Collector 2')
    credit_officer_1 = fields.Many2one('hr.employee', 'Credit Officer 1')
    credit_officer_2 = fields.Many2one('hr.employee', 'Credit Officer 2')

    sale = fields.Monetary('Sale Comm', compute="_compute_commission", currency_field='currency_id')
    field_1 = fields.Monetary('Field 1 Comm', compute="_compute_commission", currency_field='currency_id')
    field_2 = fields.Monetary('Field 2 Comm', compute="_compute_commission", currency_field='currency_id')
    co_1 = fields.Monetary('CO 1 Comm', compute="_compute_commission", currency_field='currency_id')
    co_2 = fields.Monetary('CO 2 Comm', compute="_compute_commission", currency_field='currency_id')

    company_profit = fields.Monetary('Company Profit', compute='_compute_pnl', currency_field='currency_id')
    company_expense = fields.Monetary('Company Expense', compute='_compute_pnl', currency_field='currency_id')

    def get_received_amount(self):
        for rec in self:
            if rec.received_amount:
                rec.received_amount_sub = self.currency_id.symbol + " " +str(rec.received_amount)
            else:
                rec.received_amount_sub = ""

    def _compute_pnl(self):
        for record in self:
            daa_commission = record.case_id.agreement_id.daa_commission
            company_profit = record.received_amount * daa_commission / 100

            company_expense = record.sale + record.field_1 + record.field_2 + record.co_1 + record.co_2
            company_profit -= company_expense

            record.company_profit = company_profit
            record.company_expense = company_expense

    def _compute_commission(self):
        for record in self:
            sale_commission = float(self.env['ir.config_parameter'].get_param('commission.sale_commission'))
            field_collector_commission = float(self.env['ir.config_parameter'].get_param('commission.field_collector_commission'))
            credit_officer_commission = float(self.env['ir.config_parameter'].get_param('commission.credit_officer_commission'))
            if sale_commission and record.saleperson_id and record.saleperson_id.id:
                record.sale = sale_commission * record.received_amount / 100

            if field_collector_commission and record.field_collector_1 and record.field_collector_1.id and record.field_collector_2 and record.field_collector_2.id:
                record.field_1 = field_collector_commission * record.received_amount / 100 / 2
                record.field_2 = field_collector_commission * record.received_amount / 100 / 2
            elif field_collector_commission and record.field_collector_1 and record.field_collector_1.id and (not record.field_collector_2 or not record.field_collector_2.id):
                record.field_1 = field_collector_commission * record.received_amount / 100
                record.field_2 = 0
            else:
                record.field_1 = 0
                record.field_2 = 0

            if credit_officer_commission and record.credit_officer_1 and record.credit_officer_1.id and record.credit_officer_2 and record.credit_officer_2.id:
                record.co_1 = credit_officer_commission * record.received_amount / 100 / 2
                record.co_2 = credit_officer_commission * record.received_amount / 100 / 2
            elif credit_officer_commission and record.credit_officer_1 and record.credit_officer_1.id and (not record.credit_officer_2 or not record.credit_officer_2.id):
                record.co_1 = credit_officer_commission * record.received_amount / 100
                record.co_2 = 0
            else:
                record.co_1 = 0
                record.co_2 = 0


    @api.onchange('debtor_id')
    def _onchange_debtor_id(self):
        for record in self:
            if record.debtor_id and record.debtor_id.id:
                activities = self.env['mail.activity'].search([
                    ('debtor_id', '=', record.debtor_id.id),
                    ('employee_id', '!=', False),
                ], limit=2)
                if len(activities) == 2:
                    record.field_collector_2 = activities[1].employee_id
                    record.credit_officer_2 = activities[1].employee_id
                if len(activities) >= 1:
                    record.field_collector_1 = activities[0].employee_id
                    record.credit_officer_1 = activities[0].employee_id

    # @api.depends('case_id.payment_ids.received_amount')
    # def _compute_commission_amount(self):
    #     for record in self:
    #         received_amount = 0
    #         for payment in record.case_id.payment_ids:
    #             received_amount += payment.received_amount
    #         record.received_amount = received_amount