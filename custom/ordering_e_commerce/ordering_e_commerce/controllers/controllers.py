# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging

from odoo import fields, http, tools, _
from odoo.http import request
from werkzeug.exceptions import Forbidden
from odoo.exceptions import ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class BlanketECommerce(http.Controller):
    @http.route(['/ordering'], type='http', auth="user", website=True, sitemap=False)
    def ordering_sale(self, **kw):
        Partner = request.env['res.partner']
        product_ids = request.env['product.product'].sudo().search([])
        category_ids = list(set([item.categ_id for item in product_ids]))
        partner_id = request.env.user.partner_id
        billing_id = shipping_id = partner_id
        shippings = Partner.search([('id', 'child_of', partner_id.commercial_partner_id.ids)])
        values = {
            'website': request.website,
            'product_ids': product_ids,
            'category_ids': category_ids,
            'billing_id': billing_id,
            'shipping_id': shipping_id,
            'shippings': shippings,
            'url': "/ordering/checkout",
        }
        values.update(self.checkout_values(**kw))
        return request.render("ordering_e_commerce.blanket_cart", values)

    def _get_mandatory_billing_fields(self):
        return ["name", "email", "street", "city", "country_id"]

    def _get_mandatory_shipping_fields(self):
        return ["name", "street", "city", "country_id"]

    def values_preprocess(self, order, mode, values):
        return values

    # def checkout_form_validate(self, mode, all_form_values, data):
    #     res = super(BlanketECommerce, self).checkout_form_validate()
    #     return res

    # def values_postprocess(self, order, mode, values, errors, error_msg):
    #     res = super(BlanketECommerce, self).values_postprocess()
    #     return res

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

    @http.route(['/ordering/address'], type='json', methods=['GET', 'POST'], auth="user")
    def ordering_sale_address(self, **kw):
        if not kw.get('order_id', False):
            return
        order = request.env['sale.blanket.order'].browse(kw.get('order_id'))
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        mode = kw.get('mode',(False, False))
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # # IF PUBLIC ORDER
        # if order.partner_id.id == request.env.user_id.sudo().partner_id.id:
        #     mode = ('new', 'billing')
        #     can_edit_vat = True
        #     country_code = request.session['geoip'].get('country_code')
        #     if country_code:
        #         def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
        #     else:
        #         def_country_id = request.website.user_id.sudo().country_id
        # # IF ORDER LINKED TO A PARTNER
        # else:
        shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
        if partner_id > 0:
            if partner_id == order.partner_id.id:
                mode = ('edit', 'billing')
                can_edit_vat = order.partner_id.can_edit_vat()
            else:
                if partner_id in shippings.mapped('id'):
                    mode = ('edit', 'shipping')
                else:
                    return Forbidden()
            if mode:
                values = Partner.browse(partner_id)
        elif partner_id == -1:
            mode = ('new', 'shipping')
        # else:  # no mode - refresh without post?
        #     return request.redirect('/ordering/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(order, mode, post, kw)
                billing_id = shipping_id = order.partner_id.id
                if mode[1] == 'shipping':
                    shipping_id = partner_id
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                render_values = {
                    'website_sale_order': order,
                    'billing_id': billing_id,
                    'shipping_id': shipping_id,
                    'shippings': shippings,
                }
                return {
                    'kanban': request.env['ir.ui.view'].render_template("ordering_e_commerce.address_checkout", render_values),
                    # 'payment_addess': request.env['ir.ui.view'].render_template("ordering_e_commerce.address_checkout", render_values),
                    'billing_id': billing_id,
                    'shipping_id': shipping_id,
                }

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id'])
        )
        country = country and country.id or def_country_id
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
        }
        return {'form': request.env['ir.ui.view'].render_template("ordering_e_commerce.address-form", render_values)}

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

    @http.route(['/ordering/payment'], type='json', auth="user")
    def ordering_sale_payment(self, **post):
        """ Payment step. This page proposes several payment means based on available
                payment.acquirer. State at this point :

                 - a draft sales order with lines; otherwise, clean context / session and
                   back to the shop
                 - no transaction in context / session, or only a draft one, if the customer
                   did go to a payment.acquirer website but closed the tab without
                   paying / canceling
                """
        order_id = post['blanket_order']
        order = request.env['sale.blanket.order'].browse(int(order_id))

        render_values = self._get_shop_payment_values(order, **post)

        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')

        return {
            'form':request.env['ir.ui.view'].render_template("ordering_e_commerce.payment", render_values)
        }

    @http.route(['/ordering/confirm'], type='json', auth="user")
    def ordering_sale_confirm(self, **post):
        order = post['order']
        data = {
            'partner_id': request.env.user.partner_id.id,
        }
        lines = []
        for line in order['order_line']:
            if order['order_line'][line] > 0:
                lines.append((0, 0, {
                    'product_id': int(line),
                    'product_uom_qty': order['order_line'][line]
                }))
        data['order_line'] = lines
        order_id = request.env['sale.order'].sudo().create(data)
        portal_url = order_id.get_portal_url()
        return portal_url
