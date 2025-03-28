# -*- coding:utf-8 -*-

from odoo import api, fields, models


class MoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ['account.move.line', 'mail.thread']

    notify_checked = fields.Boolean(string='Notify Checked', default=False, )

    # @api.model
    # def create(self, data):
    #     # get receivable account sum
    #     res = super(move_line, self).create(data)
    #     company = self.env['res.company'].search([], limit=1, order='id desc')[0]
    #     if not company.gst_no:
    #         account_receivable_id = self.env['ir.property'].sudo().search([('name', '=', 'property_account_receivable_id')])
    #         account_id = account_receivable_id[0].value_reference.split(',')[1]
    #
    #         amount = 0
    #         acc_mv_lines = None
    #         acc_mv_lines = self.env['account.move.line'].sudo().search([('account_id', '=', int(account_id)),
    #                                                                     ('notify_checked', '=', False)])
    #         if acc_mv_lines:
    #             amount = sum([m.balance for m in acc_mv_lines])
    #             if amount >= 1000000:
    #                 acc_mv_lines.sudo().write({'notify_checked': True})
    #                 self._notify(
    #                     u'Based on IRAS regulation, you are required to register for GST when your company revenue is $1,000,000 and above')
    #             elif 1000000 >= amount >= 800000:
    #                 acc_mv_lines.sudo().write({'notify_checked': True})
    #                 self._notify(u'Your company revenue is above $800,000, you may want to register for GST')
    #
    #     return res

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
    # Commented by Rashik
    # @api.model
    # def create(self, vals):
    #     res = super(MoveLine, self).create(vals)
    #     if not res.tax_ids:
    #         # get acc tags
    #         acc = res.account_id
    #         res.tax_ids = acc.tax_ids.ids
    #     return res

    @api.model
    def default_get(self, fields):
        vals = super(MoveLine, self).default_get(fields)
        if self.env.context.get('date',False):
            vals.update({'date_maturity':self.env.context.get('date',False)})
        return vals
