# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import api, fields, models

class FeedsConfig(models.Model):
    _name = "feeds.config"

    name = fields.Char("Name", help="name of rss feed")
    url = fields.Char("Url", help="url of rss feed")
    is_active = fields.Boolean("Is Active", help="Is Active Menu")
    sequence = fields.Integer("Sequence", help="sequence of rss feed")
    status = fields.Boolean(string='Status', default=True)
    website_ids = fields.Many2many(comodel_name='website', string="Allowed Websites")

    @api.model
    def create(self, vals):
        feedsObj = self.search([('is_active', '=', True)], order="sequence DESC", limit=1)
        if not feedsObj:
            feedsObj = self.search([], order="sequence DESC", limit=1)
            if vals['sequence'] < feedsObj.sequence:
                vals['is_active'] = True
        return super(FeedsConfig, self).create(vals)

    def write(self, vals):
        if vals.get('status'):
            if not vals.get('status'):
                for obj in self:
                    if obj.is_active:
                        feedsObj = self.search([('id', '!=', obj.id),('status', '=', True)], order="sequence DESC", limit=1)
                        if feedsObj:
                            feedsObj.is_active = True
                            vals['is_active'] = False
            else:
                for obj in self:
                    if not obj.is_active:
                        feedsObj = self.search([('id', '!=', obj.id),('status', '=', True)], order="sequence DESC", limit=1)
                        if not feedsObj:
                            vals['is_active'] = True
                            feedsObjs = self.search([('id', '!=', obj.id),('is_active', '=', True)])
                            for feedsObj in feedsObjs:
                                feedsObj.is_active = False

        return super(FeedsConfig, self).write(vals)

    def website_publish_button(self):
        self.ensure_one()
        return self.write({'status': not self.status})

    def check_request(self, requrest):
        pass
