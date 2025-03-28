# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class res_partner(models.Model):
    _inherit = "res.partner"

    customer_code = fields.Char(string="Customer Code", copy=False)
    customer_address = fields.Char(compute="get_full_address", string="Address", store="True")

    @api.constrains('customer_code')
    def _check_mail_thread(self):
        for rec in self:
            if rec.customer_code and self.search([('customer_code', '=', rec.customer_code),('id', '!=', rec.id)]):
                raise ValidationError("Customer Code must be unique!")

    def _get_name(self):
        name = super(res_partner, self)._get_name()
        name_with_customer_code = self.name
        if self.customer_code:
            name_with_customer_code = '%s (%s)' % (self.name, self.customer_code)

        name = name.replace(self.name, name_with_customer_code)
        return name

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        partner_ids = self.search(['|', ('name', operator, name),
                                   ('customer_code', operator, name)] + args,
                                  limit=limit)
        return partner_ids.name_get()

    @api.depends('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
    def get_full_address(self):
        for rec in self:
            rec.customer_address = rec.with_context(show_address_only=True, address_inline=True)._get_name()