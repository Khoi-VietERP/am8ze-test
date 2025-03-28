from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo import fields

@tagged('alphabricks', 'post_install', '-at_install')
class TestMultiplePayment(TransactionCase):

    def setUp(self):
        super(TestMultiplePayment, self).setUp()
        self.MultiplePayment = self.env['multiple.payments']
        self.AccountJournal = self.env['account.journal']
        self.AccountPayment = self.env['account.payment']

        self.journal_id = self.AccountJournal.search([('type', 'in', ('bank', 'cash'))], limit=1)
        self.currency_id = self.env.user.company_id.currency_id
        self.partner_id = self.env['res.partner'].search([], limit=1)

    def test_create_payment(self):
        # Create a new payment
        payment = self.MultiplePayment.create({
            'journal_id': self.journal_id.id,
            'payment_date': fields.Date.today(),
            'ref_no': 'test ref no',
            'partner_id': self.partner_id.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'currency_id': self.currency_id.id,
            'payment_lines': [(0, 0, {
                'name': 'test payment',
                'account_id': self.env['account.account'].search([], limit=1).id,
                'amount': 500,
            })],
        })

        # Test _compute_total method
        self.assertAlmostEqual(payment.sub_total, 500, msg="Subtotal should be accurate.")
        self.assertAlmostEqual(payment.total, 500, msg="Total should be accurate.")
        self.assertAlmostEqual(payment.amount_tax, 0, msg="GST should be accurate.")

        # Test the onchange_journal
        payment.journal_id = self.AccountJournal.create({
            'type': 'cash',
            'name': 'test_journal',
            'code': 'TEST',
            'currency_id': self.env['res.currency'].search([], limit=1).id
        })
        payment._onchange_journal()
        self.assertEqual(payment.currency_id, payment.journal_id.currency_id)

        # Test the onchange_partner_type
        payment.partner_type = 'supplier'
        payment.onchange_partner_type()
        self.assertEqual(payment.payment_type, 'outbound')

        # Post the payment and make sure it cannot be cancelled
        payment.create_payment()
        # Test if system created account.payment
        account_payment = self.AccountPayment.search([
            ('multiple_payments_line_id', 'in', payment.payment_lines.ids)
        ])
        self.assertTrue(account_payment, "Account payment not created.")
        self.assertTrue(payment.state == 'posted', "Multiple payment should posted.")
        self.assertTrue(account_payment.state == 'posted', "Account payment should posted.")

        # Unlink the multiple payment and check if account payment is also removed
        payment.unlink()
        account_payment_unlinked = self.AccountPayment.search([
            ('id', 'in', account_payment.ids)
        ])
        self.assertFalse(account_payment_unlinked, "Account payment should be removed.")
