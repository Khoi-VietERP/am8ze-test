# -*- coding: utf-8 -*-

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


# mapping invoice type to journal type

# Commented by Rashik
# class AccountInvoice(models.Model):
#     _inherit = "account.invoice"

#     tax_line_ids = fields.One2many('account.invoice.tax', 'invoice_id', string='Tax Lines', oldname='tax_line',
#                                    required=True, readonly=True, states={'draft': [('readonly', False)]}, copy=True)
