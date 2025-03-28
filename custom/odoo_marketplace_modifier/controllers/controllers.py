# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
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

import werkzeug
import odoo
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db
from odoo import http
from odoo.http import request
# from odoo.addons.web.controllers.main import binary_content
import base64
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID
from odoo.addons.website_sale.controllers.main import TableCompute, QueryURL, WebsiteSale
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website_mail.controllers.main import WebsiteMail
import logging
_logger = logging.getLogger(__name__)
import urllib.parse as urlparse
from urllib.parse import urlencode


PPG = 20  # Products Per Page
PPR = 4   # Products Per Row

SPG = 20  # Shops/sellers Per Page
SPR = 4   # Shops/sellers Per Row


marketplace_domain = [('sale_ok', '=', True), ('state', '=', "approved")]


class AuthSignupHome(odoo.addons.web.controllers.main.Home):

    def _signup_with_values(self, token, values):
        params = dict(request.params)
        is_seller = params.get('is_seller')
        if is_seller and is_seller == 'on':
            values.update({
                'mobile_no' : params.get('mobile_no',False),
                'company_address' : params.get('company_address',False),
                'street2' : params.get('street2',False),
                'postal_code' : params.get('postal_code',False),
                'membership_state' : params.get('membership_state',False),
                'uen' : params.get('uen',False),
                'name_of_ao' : params.get('name_of_ao',False),
                'official_designation' : params.get('official_designation',False),
                'date_of_acti' : params.get('date_of_acti',False),
                'receive_update' : True if params.get('receive_update',False) and params.get('receive_update',False) == 'on' else False,
                'comment' : params.get('comment',False),
            })

        is_cust = params.get('is_cust')
        if is_cust and is_cust == 'on':
            values.update({
                'is_cust' : True,
                'mobile_no': params.get('mobile_no', False),
                'company_name': params.get('company_name', False),
                'uen': params.get('uen', False),
                'staff_strength': params.get('staff_strength', False),
                'industry_sector_id': params.get('industry_sector_id', False),
                'officical_designation': params.get('officical_designation', False),
                'receive_update': True if params.get('receive_update', False) and params.get('receive_update',
                                                                                             False) == 'on' else False,
                'remarks': params.get('remarks', False),
            })
        return super(AuthSignupHome, self)._signup_with_values(token, values)

    @http.route('/cust/signup', type='http', auth="public", website=True)
    def cust_signup_form(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()
        if kw.get("name", False):
            if 'error' not in qcontext and request.httprequest.method == 'POST':
                try:
                    self.do_signup(qcontext)
                    self.web_login(*args, **kw)
                    return website_marketplace_dashboard().account()
                except UserError as e:
                    qcontext['error'] = e.name or e.value
                except (SignupError, AssertionError) as e:
                    if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                        qcontext["error"] = _("Another user is already registered using this email address.")
                    else:
                        _logger.error("%s", e)
                        qcontext['error'] = _("Could not create a new account.")

        return request.render('odoo_marketplace_modifier.mp_cust_signup', qcontext)

class website_marketplace_dashboard(http.Controller):

    @http.route('/my/marketplace', type='http', auth="public", website=True)
    def account(self):
        seller_dashboard_menu_id = request.env[
            'ir.model.data'].get_object_reference('odoo_marketplace', 'wk_seller_dashboard')[1]
        new_url = "/web#menu_id=" + str(seller_dashboard_menu_id)
        return request.redirect(new_url)