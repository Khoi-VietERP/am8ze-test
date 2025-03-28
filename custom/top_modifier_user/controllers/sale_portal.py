import binascii
from datetime import date

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.osv import expression


class CustomSaleCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self):
        values = super(CustomSaleCustomerPortal, self)._prepare_home_portal_values()
        if not request.env.user.has_group('ordering_e_commerce.group_portal_sale_order'):
            values.update({
                'quotation_count': 0,
                'order_count': 0,
            })
        return values