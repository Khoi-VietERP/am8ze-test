from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('alphabricks', 'post_install', '-at_install')
class TestSaleOrderLine(TransactionCase):
    def setUp(self):
        super(TestSaleOrderLine, self).setUp()

        # Creating records for unit test
        self.product = self.env['product.product'].create({
            'name': 'Product Test',
            'list_price': 100.0,
        })

        self.partner = self.env['res.partner'].create({'name': 'Partner Test'})

        self.order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
        })

        self.order_line = self.env['sale.order.line'].create({
            'order_id': self.order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'price_unit': self.product.list_price,
            'is_tax_inclusive': self.order.is_tax_inclusive,
        })

        # Setting tax default
        self.tax_id = self.order_line.tax_id

    def test_tax_inclusive_default_false(self):
        self.assertFalse(self.order.is_tax_inclusive, 'is_tax_inclusive in order should be false as default')
        self.assertFalse(self.order_line.is_tax_inclusive, 'is_tax_inclusive in order line should be false too')

        self.assertTrue(self.order_line.price_total == 108, 'Price total mismatch')
        self.assertTrue(self.order_line.price_tax == 8.0, 'Price tax mismatch')
        self.assertTrue(self.order_line.price_subtotal == 100, 'Price subtotal mismatch')

    def test_tax_inclusive_true(self):
        self.order.is_tax_inclusive = True

        self.assertTrue(self.order.is_tax_inclusive, 'is_tax_inclusive in order line should be true')
        self.assertTrue(self.order_line.is_tax_inclusive, 'is_tax_inclusive in order line should be true')

        self.assertTrue(self.order_line.price_total == 100, 'Price total mismatch')
        self.assertTrue(self.order_line.price_tax == 8.0, 'Price tax mismatch')
        self.assertTrue(self.order_line.price_subtotal == 92.0, 'Price subtotal mismatch')

    def test_tax_exclude_once_notax_setting(self):
        self.order.is_tax_inclusive = False
        self.order_line.tax_id = False

        self.assertFalse(self.order_line.is_tax_inclusive, 'is_tax_inclusive in order line should be false too')
        self.assertTrue(self.order_line.price_total == 100, 'Price total mismatch')
        self.assertTrue(self.order_line.price_tax == 0, 'Price tax mismatch')
        self.assertTrue(self.order_line.price_subtotal == 100, 'Price subtotal mismatch')

    def test_tax_include_once_notax_setting(self):
        self.order.is_tax_inclusive = True
        self.order_line.tax_id = False

        self.assertTrue(self.order_line.is_tax_inclusive, 'is_tax_inclusive in order line should be true')
        self.assertTrue(self.order_line.price_total == 100, 'Price total mismatch')
        self.assertTrue(self.order_line.price_tax == 0, 'Price tax mismatch')
        self.assertTrue(self.order_line.price_subtotal == 100, 'Price subtotal mismatch')

    def test_tax_exclude_once_updating_tax_setting(self):
        self.order.is_tax_inclusive = False
        self.order_line.tax_id = False
        self.order_line.tax_id = self.tax_id

        self.assertFalse(self.order_line.is_tax_inclusive, 'is_tax_inclusive in order line should be false too')
        self.assertTrue(self.order_line.price_total == 108, 'Price total mismatch')
        self.assertTrue(self.order_line.price_tax == 8, 'Price tax mismatch')
        self.assertTrue(self.order_line.price_subtotal == 100, 'Price subtotal mismatch')

    def test_tax_include_once_updating_tax_setting(self):
        self.order.is_tax_inclusive = True
        self.order_line.tax_id = False
        self.order_line.tax_id = self.tax_id

        self.assertTrue(self.order_line.is_tax_inclusive, 'is_tax_inclusive in order line should be true')
        self.assertTrue(self.order_line.price_total == 100, 'Price total mismatch')
        self.assertTrue(self.order_line.price_tax == 8, 'Price tax mismatch')
        self.assertTrue(self.order_line.price_subtotal == 92.0, 'Price subtotal mismatch')