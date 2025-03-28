# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Odoo RSS Feed Reader",
  "summary"              :  """Odoo RSS Feed Reader allows the customers to add news feeds to the Odoo. The module allows you to stay updated with the latest content, news and headlines""",
  "category"             :  "Extra Tools",
  "version"              :  "1.2.6",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-RSS-Feed-Reader.html",
  "description"          :  """Odoo RSS Feed Reader
RSS Feed
Rich Site Summary
Really Simple Syndication
Odoo Web Feed
Web Feed
News Feed
RSS Odoo
Odoo RSS
News Feed Notifications
Feed notification
News Notification
latest contents""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=odoo_rss_feed_reader",
  "depends"              :  [
                             'website_webkul_addons',
                             'wk_wizard_messages',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'views/webkul_addons_config_inherit_view.xml',
                             'views/res_config_views.xml',
                             'views/snippets.xml',
                             'views/website_templates.xml',
                             'data/data_rss_feed.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  49,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}