from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    mp_sell_page_label = fields.Char(
        string="Sell Link Label", default="Vendor", translate=True)
    mp_sellers_list_label = fields.Char(
        string="Seller List Link Label", default="Vendor List", translate=True)
    mp_seller_shop_list_label = fields.Char(
        string="Seller Shop List Link Label", default="Vendor Shop List", translate=True)

    def get_industry_sector_list(self):
        industry_sector_ids = self.env['industry.sector'].search([])
        industry_sector_list = []
        for industry_sector_id in industry_sector_ids:
            industry_sector_list.append({
                'id' : industry_sector_id.id,
                'name' : industry_sector_id.code + ' - ' + industry_sector_id.name
            })
        return industry_sector_list

    def get_date_membership_state(self):
        return [
            ('none', 'Non Member'),
            ('canceled', 'Cancelled Member'),
            ('old', 'Old Member'),
            ('waiting', 'Waiting Member'),
            ('invoiced', 'Invoiced Member'),
            ('free', 'Free Member'),
            ('paid', 'Paid Member'),
        ]

    def get_staff_strength(self):
        return self.env['staff.strength'].search([])