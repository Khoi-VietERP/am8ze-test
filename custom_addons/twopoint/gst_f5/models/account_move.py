# -*- coding:utf-8 -*-

from odoo import api, models
import calendar
from datetime import datetime, timedelta


class account_move(models.Model):
    _name = "account.move"
    _inherit = ['account.move', 'mail.thread']

    ## Comment : when moves post, it will check balance and notify
    # @api.multi
    # def post(self):
    #     res = super(account_move, self).post()
    #     ##
    #     company = self.env['res.company'].sudo().search([], limit=1, order='id desc')[0]
    #     account_config_obj = self.env['account.config.settings']
    #     lst_account_config = account_config_obj.sudo().search([], limit=1, order='id desc')
    #     if not company.gst_no and lst_account_config:
    #         account_config = lst_account_config[0]
    #         account_receivable_id = self.env['ir.property'].sudo().search(
    #             [('name', '=', 'property_account_receivable_id')])
    #         account_id = account_receivable_id[0].value_reference.split(',')[1]
    #         amount = 0
    #         acc_mv_lines = None
    #         acc_mv_lines = self.env['account.move.line'].sudo().search([('account_id', '=', int(account_id)),
    #                                                                     ('move_id.state', '=', 'posted')
    #                                                                     ])
    #         if acc_mv_lines:
    #             amount = sum([m.balance for m in acc_mv_lines])
    #             if amount < 800000:
    #                 account_config.sudo().write({'check_notify_gst_800000': False,
    #                                              'check_notify_gst_1000000': False, })
    #             elif amount >= 800000:
    #                 if amount >= 1000000 and not account_config.check_notify_gst_1000000:
    #                     account_config.sudo().write({'check_notify_gst_800000': True,
    #                                                  'check_notify_gst_1000000': True, })
    #                     self._notify(
    #                         u'Based on IRAS regulation, you are required to register for GST when your company revenue is $1,000,000 and above')
    #                 elif 1000000 > amount >= 800000 and not account_config.check_notify_gst_800000:
    #                     account_config.sudo().write({'check_notify_gst_800000': True,
    #                                                  'check_notify_gst_1000000': False, })
    #                     msg = u'Your company revenue is above $800,000, you may want to register for GST. Revenue: $ %s' % (
    #                         amount)
    #                     self._notify(msg)
    #     return res

    #

    @api.model
    def notify_gst_quarters_year(self):
        '''
        :return:
        '''
        curr_date = datetime.now()
        year = curr_date.year
        month = curr_date.month
        today = curr_date.day

        last_day_of_month = calendar.monthrange(year, month)[1]
        first_period = curr_date - timedelta(days=360)
        date_from = first_period.strftime('%Y-%m-01')
        date_to = curr_date.strftime('%Y-%m-%d')
        fourteen_before_last_day_of_month = last_day_of_month - 14

        # check config on company
        company = self.env['res.company'].search([], limit=1, order='id desc')[0]
        gst_filling_interval = company.gst_filling_interval
        if company.gst_no:
            if gst_filling_interval == 'monthly':
                if today == 1:
                    self._notify(u'You are required to file your GST F5 return within 1 month from the end of the accounting period. Log in to myTax.iras.gov.sg to file your return')
                elif today == fourteen_before_last_day_of_month:
                    self._notify(u'The filing deadline for your GST F5 return is approaching soon. To avoid costly penalties, log in to myTax.iras.gov.sg to file your return on time if you have not done so.')
            elif gst_filling_interval == 'quarterly':
                if month in [2,5,8,11]:
                    if today == 1:
                        self._notify(u'You are required to file your GST F5 return within 1 month from the end of the accounting period. Log in to myTax.iras.gov.sg to file your return')
                    elif today == fourteen_before_last_day_of_month:
                        self._notify(u'The filing deadline for your GST F5 return is approaching soon. To avoid costly penalties, log in to myTax.iras.gov.sg to file your return on time if you have not done so.')
            elif gst_filling_interval == 'quarterly2':
                if month in [3,6,9,12]:
                    if today == 1:
                        self._notify(u'You are required to file your GST F5 return within 1 month from the end of the accounting period. Log in to myTax.iras.gov.sg to file your return')
                    elif today == fourteen_before_last_day_of_month:
                        self._notify(u'The filing deadline for your GST F5 return is approaching soon. To avoid costly penalties, log in to myTax.iras.gov.sg to file your return on time if you have not done so.')
            elif gst_filling_interval == 'quarterly3':
                if month in [1,4,7,10]:
                    if today == 1:
                        self._notify(u'You are required to file your GST F5 return within 1 month from the end of the accounting period. Log in to myTax.iras.gov.sg to file your return')
                    elif today == fourteen_before_last_day_of_month:
                        self._notify(u'The filing deadline for your GST F5 return is approaching soon. To avoid costly penalties, log in to myTax.iras.gov.sg to file your return on time if you have not done so.')

#         account_receivable_id = self.env['ir.property'].sudo().search(
#                 [('name', '=', 'property_account_receivable_id')])
#
#         for account in account_receivable_id:
#             if account.value_reference.split(',')[0] == 'account.account':
#                 account.value_reference.split(',')[0]
#                 print ">>>>>>>>>>>>>>>>>>. ANBAUAUGJHGVHGJH"\
        accountType = self.env['account.account.type'].search([('type','=',['other']),('name','in',['Other Income','Cost of Revenue'])]).ids
        account_id = self.env['account.account'].search([('user_type_id','in',accountType)]).ids

        if (today == 1) and (month == 1):
        # if (today == last_day_of_month) and (month % 3 == 0):
        #if (month % 3 == 0):
            account_receivable_id = self.env['ir.property'].sudo().search(
                [('name', '=', 'property_account_receivable_id')])
            #if account_receivable_id:
            if account_id:
        #        account_id = account_receivable_id[0].value_reference.split(',')[1]
                acc_mv_lines = self.env['account.move.line'].sudo().search([('account_id', 'in', account_id),
                                                                            ('move_id.state', '=', 'posted'),
                                                                            ('date', '>=', date_from),
                                                                            ('date', '<=', date_to),
                                                                            ])
                amount = sum([m.balance for m in acc_mv_lines])
                if amount > 1000000:
                    msg = u""" Businesses whose taxable turnover have exceeded $1 million are required to register for GST. This is computed
                                based on the taxable turnover for any four consecutive calendar quarters. Deadline to register with IRAS is 30 days
                                from the last quarter. As your income has exceeded $1 million for four quarters, you should review whether your
                                income is taxable for GST purposes and whether you are required to register for GST.
                    """
                    self._notify(msg)

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
            channel_id.with_context(ctx).message_post(subject='GST Registration', body=msg,
                                                      subtype="mail.mt_comment", partner_ids=lst_partner)
        except Exception:
            pass
