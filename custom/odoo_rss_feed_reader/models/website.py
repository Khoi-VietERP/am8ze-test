# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import api, fields, models
import feedparser
import re

class Website(models.Model):
    _inherit = "website"

    def getBody(self, feedsConfigObjs, rss=''):
        searchFilter = [('is_active', '=', True), ('status', '=', True)]
        if rss:
            searchFilter.append(('name', '=', rss))
        feedsObj = self.env['feeds.config'].search(searchFilter, order="sequence DESC", limit=1)
        data = []
        if feedsObj:
            if feedsConfigObjs:
                feedUrl = feedsObj[0].url
                feeds = feedparser.parse(feedUrl)
                feeds_limit = self.getLimit(feedsConfigObjs.feeds_limit)
                feeds_char_limit = self.getLimit(feedsConfigObjs.feeds_char_limit)
                if feeds:
                    count = 0
                    entries = feeds.entries
                    regex = re.compile('<.*?>')
                    for entity in entries:
                        if feeds_limit == count:
                            break
                        count = count + 1
                        published = ''
                        description = ''
                        if feedsConfigObjs.show_description:
                            try:
                                description = entity.description
                                description = re.sub(regex, '', description[0:feeds_char_limit])
                            except:
                                pass
                            finally:
                                pass
                        if feedsConfigObjs.show_date:
                            try:
                                published = entity.published
                                if published:
                                    published = published.rsplit(' ', 2)[0]
                            except:
                                pass
                            finally:
                                pass
                        data.append({"rss_menu_title":entity.title, "rss_menu_link":entity.link, "rss_menu_date":published, "rss_menu_description":description})
        return data

    def getLimit(self, val):
        if isinstance(val, str):
            try:
                val = int(val)
            except ValueError:
                val = 0
        return val
