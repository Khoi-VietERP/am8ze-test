# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.website.controllers.main import Website
from odoo.http import request
import werkzeug.utils
import werkzeug.wrappers

class Am8zeUrlRedirect(Website):

    @http.route('/website/lang/<lang>', type='http', auth="public", website=True, multilang=False)
    def change_lang(self, lang, r='/', **kwargs):
        """ :param lang: supposed to be value of `url_code` field """
        if lang == 'default':
            lang = request.website.default_lang_id.url_code
            r = '/%s%s' % (lang, r or '/')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if base_url not in r:
            if r and r[0] == '/':
                r = base_url + r
            else:
                values = {
                    'new_url': r,
                    'back_url' : base_url
                }
                return request.render("redirect_internal_only.redirect_confirm_template", values)

        redirect = werkzeug.utils.redirect(r or ('/%s' % lang), 303)
        lang_code = request.env['res.lang']._lang_get_code(lang)
        redirect.set_cookie('frontend_lang', lang_code)
        return redirect