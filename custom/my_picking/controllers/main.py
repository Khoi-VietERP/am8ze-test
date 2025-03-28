# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

class PortalAccount(CustomerPortal):

    def get_partner_list(self):
        partner_id = request.env.user.partner_id
        child_ids = request.env['res.partner'].sudo().search([('parent_id', '=', partner_id.id)])
        partner_list = partner_id.ids + child_ids.ids
        return partner_list

    def _prepare_home_portal_values(self):
        values = super(PortalAccount, self)._prepare_home_portal_values()
        partner_list = self.get_partner_list()
        picking_count = request.env['stock.picking'].sudo().search_count([
            ('picking_type_id.code', '=', 'outgoing'),
            ('partner_id', 'in', partner_list),
        ])
        values['picking_count'] = picking_count
        return values

    # def _prepare_home_portal_values(self):
    #     values = super(PortalAccount, self)._prepare_home_portal_values()
    #     picking_count = request.env['stock.picking'].search_count([
    #         ('picking_type_id.code', '=', 'outgoing'),
    #     ]) if request.env['stock.picking'].check_access_rights('read', raise_exception=False) else 0
    #     values['picking_count'] = picking_count
    #     return values

    def _picking_get_page_view_values(self, picking, access_token, **kwargs):
        values = {
            'page_name': 'picking',
            'picking': picking,
        }
        return self._get_page_view_values(picking, access_token, values, 'my_pickings_history', False, **kwargs)


    @http.route(['/my/pickings', '/my/pickings/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_pickings(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        StockPicking = request.env['stock.picking'].sudo()
        partner_list = self.get_partner_list()

        domain = [('picking_type_id.code', '=', 'outgoing'),('partner_id', 'in', partner_list)]

        searchbar_sortings = {
            'scheduled_date': {'label': _('Scheduled Date'), 'order': 'scheduled_date desc'},
        }
        # default sort by order
        if not sortby:
            sortby = 'scheduled_date'
        order = searchbar_sortings[sortby]['order']

        # archive_groups = self._get_archive_groups('account.move', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        picking_count = StockPicking.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/pickings",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=picking_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        pickings = StockPicking.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_pickings_history'] = pickings.ids[:100]

        values.update({
            'date': date_begin,
            'pickings': pickings,
            'page_name': 'picking',
            'pager': pager,
            # 'archive_groups': archive_groups,
            'default_url': '/my/pickings',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("my_picking.portal_my_pickings", values)

    @http.route(['/my/pickings/<int:picking_id>'], type='http', auth="public", website=True)
    def portal_my_picking_detail(self, picking_id, access_token=None, report_type=None, download=False, **kw):
        try:
            picking_sudo = self._document_check_access('stock.picking', picking_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=picking_sudo, report_type=report_type, report_ref='stock.action_report_delivery',
                                     download=download)

        values = self._picking_get_page_view_values(picking_sudo, access_token, **kw)
        # acquirers = values.get('acquirers')
        # if acquirers:
        #     country_id = values.get('partner_id') and values.get('partner_id')[0].country_id.id
        #     values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(picking_sudo.amount_residual,
        #                                                                  picking_sudo.currency_id, country_id)

        return request.render("my_picking.portal_picking_page", values)