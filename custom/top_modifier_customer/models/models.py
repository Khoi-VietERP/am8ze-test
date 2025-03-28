# -*- coding: utf-8 -*-

from odoo import models, fields, api


class res_partner(models.Model):
   _inherit = 'res.partner'

   @api.model
   def get_partner_company(self):
       return self.env.user.company_id
