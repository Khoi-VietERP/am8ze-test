# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.common.partner.report"
    _name = "account.report.partner.ledger"
    _description = "Account Partner Ledger"

    amount_currency = fields.Boolean(
        "With Currency",
        help="It adds the currency column on report if the "
        "currency differs from the company currency.")
    reconciled = fields.Boolean('Reconciled Entries')

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update(
            {'reconciled': self.reconciled,
             'amount_currency': self.amount_currency})
        return self.env.ref(
            'sg_account_report.'
            'action_report_partnerledger').report_action(self, data=data)
