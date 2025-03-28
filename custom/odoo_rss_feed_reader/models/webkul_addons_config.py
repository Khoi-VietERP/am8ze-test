# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import fields, models, api, _


class WebkulWebsiteAddons(models.TransientModel):
    _inherit = 'webkul.website.addons'

    module_odoo_rss_feed_reader = fields.Boolean(
        string="Odoo RSS Feed Reader")

    def get_rss_feed_configuration_view(self):
        self.ensure_one()
        googleAdsenseConfigObjs = self.env['rss.feed.config.settings'].search([])
        imd = self.env['ir.model.data']
        actionObj = imd.xmlid_to_object('odoo_rss_feed_reader.action_rss_feed_config_conf')
        treeId = imd.xmlid_to_res_id('odoo_rss_feed_reader.view_rss_feed_config_settings_tree')
        formId = imd.xmlid_to_res_id('odoo_rss_feed_reader.rss_feed_config_conf_view')

        result = {
            'name': actionObj.name,
            'help': actionObj.help,
            'type': actionObj.type,
            'views': [[treeId, 'tree'], [formId, 'form']],
            'target': actionObj.target,
            'context': actionObj.context,
            'res_model': actionObj.res_model,
        }
        if len(googleAdsenseConfigObjs) == 1:
            result['views'] = [(formId, 'form')]
            result['res_id'] = googleAdsenseConfigObjs[0].id
        return result
