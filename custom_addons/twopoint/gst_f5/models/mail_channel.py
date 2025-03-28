# -*- coding:utf-8 -*-

from odoo import api, models


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    @api.model
    def add_user_gst_channel(self):
        partner_gst = self.env.ref('gst_f5.partner_gst')
        channel_gst = self.env.ref('gst_f5.channel_gst')
        if partner_gst and channel_gst:
            channel_gst.sudo().write({'channel_partner_ids': [(4, partner_gst.id)]})



