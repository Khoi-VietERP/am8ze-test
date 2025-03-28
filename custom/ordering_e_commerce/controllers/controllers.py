# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging

from odoo import fields, http, tools, _, api, SUPERUSER_ID
from odoo.http import request
from werkzeug.exceptions import Forbidden
from odoo.exceptions import ValidationError, AccessError, MissingError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


from odoo.addons.sale.controllers.portal import CustomerPortal

class BlanketECommerce(http.Controller):

    @http.route(['/ordering'], type='http', auth="user", website=True, sitemap=False)
    def ordering_sale(self, **kw):
        Partner = request.env['res.partner']
        product_ids = request.env['product.product'].sudo().search([('show_in_ordering','=',True)]).sorted(key='ordering_sequence', reverse=False)
        category_ids = list(set([item.categ_id.id for item in product_ids]))
        category_ids = request.env['product.category'].sudo().browse(category_ids).sorted(key='ordering_sequence', reverse=False)
        partner_id = request.env.user.partner_id
        billing_id = shipping_id = partner_id
        shippings = Partner.search([('id', 'child_of', partner_id.commercial_partner_id.ids)])
        pricelist = partner_id.property_product_pricelist
        list_prices = {}
        for product_id in product_ids:
            first_possible_combination = product_id.product_tmpl_id._get_first_possible_combination()
            combination_info = product_id.product_tmpl_id._get_combination_info(first_possible_combination, add_qty=1, pricelist=pricelist)
            list_prices.update({
                str(product_id.id) : combination_info['price']
            })

        values = {
            'pricelist': pricelist,
            'website': request.website,
            'is_portal_price': request.env.user.has_group('ordering_e_commerce.group_portal_price'),
            'product_ids': product_ids,
            'category_ids': category_ids,
            'billing_id': billing_id,
            'shipping_id': shipping_id,
            'shippings': shippings,
            'list_prices': list_prices,
            'url': "/ordering/checkout",
        }
        values.update(self.checkout_values(**kw))
        return request.render("ordering_e_commerce.blanket_cart", values)

    @http.route(['/ordering/get_gift'], type='json', auth="user")
    def get_ordering_gift(self, **kw):
        pricelist_id = kw.get('pricelist_id')
        order_data = kw.get('order_data')
        step = kw.get('step')
        ordering_gift = request.env['sale.order'].get_ordering_gift(pricelist_id, order_data)
        if step == 20:
            return request.env['ir.ui.view'].render_template('ordering_e_commerce.table_ordering_gift', ordering_gift)
        if step == 10:
            product_rule_ids = ordering_gift.get('product_rule_ids', [])
            summary_gift_line = []
            for product_rule_id in product_rule_ids:
                template_gift_line = request.env['ir.ui.view'].render_template('ordering_e_commerce.line_ordering_gift', {'product_rule_id' : product_rule_id, 'price' : 0.0})
                summary_gift_line.append({
                    'template_gift_line' : template_gift_line,
                    'product_id' : product_rule_id['product_id'].id,
                })
            return summary_gift_line

    def _get_mandatory_billing_fields(self):
        return ["name", "email", "street", "city", "country_id"]

    def _get_mandatory_shipping_fields(self):
        return ["name", "street", "city", "country_id"]

    def values_preprocess(self, order, mode, values):
        return values

    def checkout_form_validate(self, mode, all_form_values, data):
        # mode: tuple ('new|edit', 'billing|shipping')
        # all_form_values: all values before preprocess
        # data: values after preprocess
        error = dict()
        error_message = []

        # Required fields from form
        required_fields = [f for f in (all_form_values.get('field_required') or '').split(',') if f]
        # Required fields from mandatory field function
        required_fields += mode[1] == 'shipping' and self._get_mandatory_shipping_fields() or self._get_mandatory_billing_fields()
        # Check if state required
        country = request.env['res.country']
        if data.get('country_id'):
            country = country.browse(int(data.get('country_id')))
            if 'state_code' in country.get_address_fields() and country.state_ids:
                required_fields += ['state_id']

        # error message for empty required fields
        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        # vat validation
        Partner = request.env['res.partner']
        if data.get("vat") and hasattr(Partner, "check_vat"):
            if data.get("country_id"):
                data["vat"] = Partner.fix_eu_vat_number(data.get("country_id"), data.get("vat"))
            partner_dummy = Partner.new({
                'vat': data['vat'],
                'country_id': (int(data['country_id'])
                               if data.get('country_id') else False),
            })
            try:
                partner_dummy.check_vat()
            except ValidationError:
                error["vat"] = 'error'

        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message

    def _checkout_form_save(self, order, mode, checkout, all_values):
        Partner = request.env['res.partner']
        partner_id = Partner
        if mode[0] == 'new':
            partner_id = Partner.sudo().create(checkout).id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                # double check
                shippings = Partner.sudo().search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return Forbidden()
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id

    def values_postprocess(self, order, mode, values, errors, error_msg):
        new_values = {}
        authorized_fields = request.env['ir.model']._get('res.partner')._get_form_writable_fields()
        team_id = request.env['crm.team'].search([('name','=','Website')],limit=1)
        if not team_id:
            team_id = request.env['crm.team'].create({'name':'Website'})
        for k, v in values.items():
            # don't drop empty value, it could be a field to reset
            if k in authorized_fields and v is not None:
                new_values[k] = v
            else:  # DEBUG ONLY
                if k not in ('field_required', 'partner_id', 'callback', 'submitted'): # classic case
                    _logger.debug("website_sale postprocess: %s value has been dropped (empty or not writable)" % k)

        new_values['customer'] = True
        new_values['team_id'] = team_id.id
        new_values['user_id'] = order.partner_id.user_id and order.partner_id.user_id.id

        # if request.website.specific_user_account:
        #     new_values['website_id'] = request.website.id

        if mode[0] == 'new':
            new_values['company_id'] = order.company_id.id

        lang = request.lang
        if lang:
            new_values['lang'] = lang
        if mode == ('edit', 'billing') and order.partner_id.type == 'contact':
            new_values['type'] = 'other'
        if mode[1] == 'shipping':
            new_values['parent_id'] = order.partner_id.commercial_partner_id.id
            new_values['type'] = 'delivery'

        return new_values, errors, error_msg

    def checkout_values(self, **kw):
        partner_id = request.env.user.partner_id
        Partner = partner_id.with_context(show_address=1).sudo()
        shippings = Partner.search([
            ("id", "child_of", partner_id.commercial_partner_id.ids),
            '|', ("type", "in", ["delivery", "other"]), ("id", "=", partner_id.commercial_partner_id.id)
        ], order='id desc')
        if shippings:
            if kw.get('partner_id') or 'use_billing' in kw:
                if 'use_billing' in kw:
                    partner_id = partner_id.id
                else:
                    partner_id = int(kw.get('partner_id'))

        values = {
            'shippings': shippings,
            'mode': ('edit', 'billing'),
            'error': {
                'error_message': []
            }
        }
        return values

    def _get_shop_payment_values(self, order, **kwargs):
        partner_id = request.env.user.partner_id
        Partner = partner_id.with_context(show_address=1).sudo()
        shipping_id = kwargs.get('shipping_address', False)
        shipping_id = shipping_id != -1 and Partner.browse(shipping_id) or partner_id

        values = dict(
            website_sale_order=order,
            errors=[],
            partner=partner_id.id,
            order=order,
            shipping_id=shipping_id,
            payment_action_id=request.env.ref('payment.action_payment_acquirer').id,
            return_url= '/shop/payment/validate',
            bootstrap_formatting= True
        )

        domain = expression.AND([
            ['&', ('website_published', '=', True), ('company_id', '=', order.company_id.id)],
            ['|', ('specific_countries', '=', False), ('country_ids', 'in', [partner_id.country_id.id])]
        ])
        acquirers = request.env['payment.acquirer'].search(domain)
        values['acquirers'] = [acq for acq in acquirers if (acq.payment_flow == 'form' and acq.view_template_id) or
                                    (acq.payment_flow == 's2s' and acq.registration_view_template_id)]
        values['tokens'] = request.env['payment.token'].search(
            [('partner_id', '=', partner_id.id),
            ('acquirer_id', 'in', acquirers.ids)])

        return values

    def _document_check_access(self, model_name, document_id, access_token=None):
        document = request.env[model_name].browse([document_id])
        document_sudo = document.with_user(SUPERUSER_ID).exists()
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except AccessError:
            if not access_token or not document_sudo.access_token or not consteq(document_sudo.access_token, access_token):
                raise
        return document_sudo

    # @http.route(['/ordering/gift/<int:order_id>'], type='http', auth="user", website=True, sitemap=False)
    # def ordering_gift(self, order_id, access_token=None, **post):
    #     try:
    #         order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
    #     except (AccessError, MissingError):
    #         return request.redirect('/my')
    #
    #     portal_url = order_sudo.get_portal_url()
    #     if order_sudo.state != 'draft':
    #         return request.redirect(portal_url)
    #
    #     check_ordering_gift = order_sudo.check_ordering_gift()
    #     if not check_ordering_gift['has_rule']:
    #         order_sudo.action_confirm()
    #         return request.redirect(portal_url)
    #     else:
    #         return request.render("ordering_e_commerce.ordering_gift", {'gift': check_ordering_gift, 'url': '/ordering/gift/confirm/%d' % order_sudo.id})

    @http.route(['/ordering/gift/confirm/<int:order_id>'], type='http', auth="user", website=True, sitemap=False)
    def ordering_gift_confirm(self, order_id, access_token=None, **post):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        portal_url = order_sudo.get_portal_url()
        if order_sudo.state != 'draft':
            request.redirect(portal_url)

        check_ordering_gift = order_sudo.check_ordering_gift()
        if check_ordering_gift['has_rule']:
            lines = []
            for item in post:
                if 'amount' in item:
                    _item = item.split('_')
                    if len(_item) == 3:
                        rule_id = int(_item[2])
                        existed_rule = [i for i in check_ordering_gift['amount_rule_ids'] if i.id == rule_id]
                        if existed_rule:
                            lines.append((0, 0, {
                                'product_id': existed_rule[0].product_gift_id.id,
                                'product_uom_qty': existed_rule[0].product_gift_quantity,
                                'price_unit': 0,
                            }))
                elif 'product' in item:
                    _item = item.split('_')
                    if len(_item) == 3:
                        rule_id = int(_item[2])
                        existed_rule = [i for i in check_ordering_gift['product_rule_ids'] if i['id'] == rule_id]
                        if existed_rule:
                            lines.append((0, 0, {
                                'product_id': existed_rule[0]['product_gift_id'].id,
                                'product_uom_qty': existed_rule[0]['product_gift_quantity'],
                                'price_unit' : 0,
                            }))
            order_sudo.write({'order_line': lines})
        order_sudo.action_confirm()
        return request.redirect(portal_url)

    @http.route(['/ordering/confirm'], type='json', auth="user")
    def ordering_sale_confirm(self, **post):
        order = post['order']
        po_number = post['po_number']
        remarks = post['remarks']
        data = {
            'partner_id': request.env.user.partner_id.id,
            'po_number': po_number,
            'note': remarks,
        }
        lines = []
        for line in order['order_line']:
            if order['order_line'][line] and order['order_line'][line]['qty'] > 0:
                lines.append((0, 0, {
                    'product_id': int(line),
                    'product_uom_qty': order['order_line'][line]['qty'],
                    # 'tax_id': [(6, 0, [])],
                    # 'remarks': order['order_line'][line]['remarks'],
                }))
        data['order_line'] = lines
        order_id = request.env['sale.order'].sudo().create(data)
        check_ordering_gift = order_id.check_ordering_gift()
        data_redirect = {
            'has_rule' : check_ordering_gift['has_rule'],
            'url' : '/ordering/gift/confirm/%d' % order_id.id,
            'order_id' : order_id.id
        }
        return data_redirect
