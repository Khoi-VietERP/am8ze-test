# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PragtechSocialPost(models.Model):

    _name = 'pragtech.social.post'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Pragtech Social Post'

    @api.model
    def default_get(self, fields):
        res = super(PragtechSocialPost, self).default_get(fields)
        psa_ids = self.env['pragtech.social.account'].search([])
        res.update({
            'social_account_ids': [(6, 0, psa_ids.ids)],
            'account_media_ids': [(6, 0, psa_ids.mapped('social_media_id').ids)],
        })
        return res

    name = fields.Char(
        string='Name')
    post_message = fields.Text(
        string="Message",
        required=True)
    social_account_ids = fields.Many2many(
        'pragtech.social.account')
    post_image_ids = fields.Many2many(
        'ir.attachment', string='Post Attach Images')
    account_media_ids = fields.Many2many(
        'pragtech.social.media')
