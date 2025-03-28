# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import http, tools,api, _
from odoo.http import request
from odoo.addons.web.controllers.main import WebClient, Binary, Home
import feedparser
import logging
_logger = logging.getLogger("===RSS LOS ===")

class Website(Home):

    @http.route(['/feed'], type='http', auth="public", website=True)
    def feed(self, **kw):
        page = 'feed'
        try:
            request.website.get_template('odoo_rss_feed_reader.feed').name
        except Exception as e:
            return request.env['ir.http']._handle_exception(e, 404)
        return request.render('odoo_rss_feed_reader.feed', {})

    @http.route(['/get/rss/data'], type='json', auth="public", methods=['POST'], website=True)
    def get_rss_data(self, rss='', **kw):
        data = []
        feedsObjs = request.env['feeds.config'].search([('status', '=', True)], order="sequence DESC").filtered(lambda f: request.website.id in f.website_ids.ids or not f.website_ids)
        if len(feedsObjs) == 0:
            feed_blank_page = self.getErrorMessage()
            return {'response':'error', 'data':feed_blank_page}
        feedsConfigObjs = request.env['rss.feed.config.settings'].search([('is_active', '=', True), ('website_id', '=', request.website.id)], limit=1)
        if rss:
            for feedsObj in feedsObjs:
                if feedsObj.name == rss:
                    feedsObj.sudo().is_active = True
                    if feedsObj:
                        data = request.env['website'].getBody(feedsConfigObjs, rss)
                else:
                    feedsObj.sudo().is_active = False
        else:
            data = request.env['website'].getBody(feedsConfigObjs)
        data_grid = ''
        try:
            renderTemplate = 'odoo_rss_feed_reader.wk_rss_menu_view' if feedsConfigObjs.rss_view == 'menu' else 'odoo_rss_feed_reader.wk_rss_card_view' if feedsConfigObjs.rss_view == 'card' else 'odoo_rss_feed_reader.s_rss_sleek'
            data_grid = request.env['ir.ui.view'].render_template(renderTemplate, {'rssdata': data})
        except Exception as e:
            _logger.info("======Exception===== : %r", e)
        return {'response':'success', 'data':data_grid}

    def getErrorMessage(self):
        feed_blank_page = request.env['ir.default'].sudo().get('rss.feed.config.settings', 'feed_blank_page')
        if not feed_blank_page:
            feed_blank_page = 'Currenty all rss feeds are disabled or might be there have no feeds are present. Please contact administrator to check current feeds.'
        return feed_blank_page

    def getLimit(self, val):
        if isinstance(val, str):
            try:
                val = int(val)
            except ValueError:
                val = 0
        return val
