# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountingCommonPartnerReport(models.TransientModel):
    _name = 'account.common.partner.report'
    _description = 'Account Common Partner Report'
    _inherit = "account.common.report"

    result_selection = fields.Selection(
        [('customer', 'Receivable Accounts'),
         ('supplier', 'Payable Accounts'),
         ('customer_supplier', 'Receivable and Payable Accounts')],
        string="Partner's",
        required=True,
        default='customer')

    def pre_print_report(self, data):
        """Print the report."""
        data['form'].update(self.read(['result_selection'])[0])
        return data
