# -*- coding:utf-8 -*-

import calendar
from datetime import datetime

from odoo import api, fields, models


class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = ['res.company', 'mail.thread']

    gst_no = fields.Char('GST No', size=64, related='partner_id.vat')
    gst_filling_interval = fields.Selection(
        [
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly 1'),
            ('quarterly2', 'Quarterly 2'),
            ('quarterly3', 'Quarterly 3'),
        ], index=True,
        string="GST Filing Interval",
    )

    prompt_user_ids = fields.Many2many('res.users', string='Prompt')

    @api.model
    def add_user_company(self):
        user_gst = self.env.ref('gst_f5.user_gst')
        company = self.env['res.company'].sudo().search([], limit=1, order='id desc')[0]
        if user_gst and company:
            company.sudo().write({'prompt_user_ids': [(4, user_gst.id)]})


    @api.model
    def _get_customer_receivables(self, date_from, date_to):
        '''
        Get customer receivables
        :return:
        '''
        # get receivable account sum
        account_receivable_id = self.env['ir.property'].search([('name', '=', 'property_account_receivable_id')])
        account_id = account_receivable_id[0].value_reference.split(',')[1]

        amount = 0
        acc_mv_lines = None
        if date_from and date_to:
            acc_mv_lines = self.env['account.move.line'].search(
                [('account_id', '=', int(account_id)), ('date', '<=', date_to), ('date', '>=', date_from)])

        if acc_mv_lines:
            amount = sum([m.balance for m in acc_mv_lines])

        return amount

    @api.model
    def _notify(self, msg):
        '''
        notify with msg
        :param msg:
        :return:
        '''
        context = self._context or {}
        ctx = context.copy()
        ctx['mail_notify_author'] = True
        user_ids = self.env['res.company'].sudo().search([], limit=1, order='id desc')[0]
        lst_user = user_ids.prompt_user_ids
        lst_partner = [u.partner_id.id for u in lst_user]
        channel_id = self.env['ir.model.data'].xmlid_to_object('gst_f5.channel_gst')
        try:
            channel_id.sudo().with_context(ctx).message_post(subject='GST Registration', body=msg, subtype="mail.mt_comment", partner_ids=lst_partner)
        except Exception:
            pass

    @api.model
    def notify_gst(self):
        '''
        Prompt partner about gst filling
        :return:
        '''
        curr_date = datetime.now()
        year = curr_date.year
        month = curr_date.month
        today = curr_date.day
        last_day_of_month = calendar.monthrange(year, month)[1]
        # check config on company
        company = self.env['res.company'].search([], limit=1, order='id desc')[0]
        gst_filling_interval = company.gst_filling_interval
        if company.gst_no:
            if gst_filling_interval == 'monthly':
                if today == last_day_of_month:
                    self._notify(u'Please be reminded to file your GST')
            elif gst_filling_interval == 'quarterly':
                if (today == last_day_of_month) and (month % 3 == 0):
                    self._notify(u'Please be reminded to file your GST')
        else:
            account_receivable_id = self.env['ir.property'].sudo().search(
                [('name', '=', 'property_account_receivable_id')])
            account_id = account_receivable_id[0].value_reference.split(',')[1]

            amount = 0
            acc_mv_lines = None
            acc_mv_lines = self.env['account.move.line'].sudo().search([('account_id', '=', int(account_id))])
            if acc_mv_lines:
                amount = sum([m.balance for m in acc_mv_lines])
                if amount >= 1000000:
                    acc_mv_lines.sudo().write()
                    self._notify(
                        u'Based on IRAS regulation, you are required to register for GST when your company revenue is $1,000,000 and above')
                elif 1000000 >= amount >= 800000:
                    acc_mv_lines.sudo().write()
                    self._notify(u'Your company revenue is above $800,000, you may want to register for GST')

    @api.onchange('gst_no', 'gst_filling_interval')
    def onchange_gst_no(self):
        if self.gst_no:
            gst_no = self.gst_no
            if gst_no.isspace() or not self.gst_no:
                self.gst_no = ''
                self.gst_filling_interval = False
        else:
            self.gst_filling_interval = False
