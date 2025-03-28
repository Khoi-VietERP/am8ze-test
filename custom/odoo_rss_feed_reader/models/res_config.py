# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import api, fields, models

class RssFeedConfigSettings(models.Model):
    _name = 'rss.feed.config.settings'
    _description = "RSS Feed Config Settings"

    def _default_website(self):
        return self.env['website'].search([], limit=1)

    website_id = fields.Many2one('website', string="Website", default=_default_website)
    name = fields.Char(string="Name", required=True)
    is_active = fields.Boolean(string="Active on website", default=False, copy=False)
    feed_title = fields.Char('Feed Title', translate=True,
                            help="Title for rss feed page", default="RSS Feeds")
    rss_view = fields.Selection([
                                ('sleek', 'Sleek View'),
                                ('card', 'Card View'),
                                ('menu', 'Menu View')
                            ],
                            'RSS View Type',
                            help="RSS page view as per as selection")
    feeds_limit = fields.Char('Feeds Limit',
                            help="Maximum number of feeds for every rss feed", default=4)
    feeds_char_limit = fields.Char('Feeds Character Limit',
                            help="Maximum character for description of every feed")
    show_date = fields.Boolean('Show Datetime',
                            help="Enable if willing to show date on rss tab")
    show_description = fields.Boolean('Show Description',
                            help="Enable if willing to show description on rss tab")
    feed_blank_page = fields.Text('Blank Page Message',
                            help="This message will be visible in feed page in case there have no feeds or all feeds are disabled")

    @api.model
    def create_wizard(self):
        wizard_id = self.env['website.message.wizard'].create({'message': _("Currently another Configuration Setting for Odoo RSS Feed is active. You can not active other Configuration Setting. So, If you want to deactive the previous active configuration setting and active new configuration then click on 'Deactive Previous And Active New' button else click on 'cancel'.")})
        return {
            'name': _("Odoo RSS FEED"),
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'website.message.wizard',
            'res_id': wizard_id.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new'
        }

    def toggle_is_active(self):
        for record in self:
            active_ids = self.search([('is_active', '=', True), ('id', '!=', record.id), ('website_id', '=', record.website_id.id)])
            if active_ids:
                return self.create_wizard()
            record.is_active = not record.is_active
