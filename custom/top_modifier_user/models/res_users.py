# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    show_price_web_portal = fields.Boolean('Show Price Web/ Portal')
    show_portal_invoice_bill = fields.Boolean('Show Invoices &amp; Bills in Web / Portal')
    show_portal_sale_order = fields.Boolean('Show Sale Order in Web / Portal')

    def _subscribe_show_price_web_portal(self, show_price_web_portal):
        group_id = self.env.ref('ordering_e_commerce.group_portal_price')
        data = []
        for record in self:
            if record.show_price_web_portal:
                data.append((4,record.id))
            else:
                data.append((3,record.id))
        group_id.write({'users':data})

    def _subscribe_show_portal_invoice_bill(self, show_portal_invoice_bill):
        group_id = self.env.ref('ordering_e_commerce.group_portal_invoice_bill')
        data = []
        for record in self:
            if record.show_portal_invoice_bill:
                data.append((4,record.id))
            else:
                data.append((3,record.id))
        group_id.write({'users':data})

    def _subscribe_show_portal_sale_order(self, show_portal_sale_order):
        group_id = self.env.ref('ordering_e_commerce.group_portal_sale_order')
        data = []
        for record in self:
            if record.show_portal_sale_order:
                data.append((4,record.id))
            else:
                data.append((3,record.id))
        group_id.write({'users':data})

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if 'show_price_web_portal' in vals:
            self._subscribe_show_price_web_portal(vals.get('show_price_web_portal', False))
        if 'show_portal_invoice_bill' in vals:
            self._subscribe_show_portal_invoice_bill(vals.get('show_portal_invoice_bill', False))
        if 'show_portal_sale_order' in vals:
            self._subscribe_show_portal_sale_order(vals.get('show_portal_sale_order', False))
        return res
