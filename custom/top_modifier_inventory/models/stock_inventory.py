# -*- coding: utf-8 -*-

from odoo import models, fields, api


class stock_inventory(models.Model):
    _inherit = 'stock.inventory'

    show_all = fields.Boolean(string="Include show product quantity equal to zero")

    def _get_all_inventory_lines_values(self):
        # TDE CLEANME: is sql really necessary ? I don't think so
        locations = self.env['stock.location']
        if self.location_ids:
            locations = self.env['stock.location'].search([('id', 'child_of', self.location_ids.ids)])
        else:
            locations = self.env['stock.location'].search([('company_id', '=', self.company_id.id), ('usage', 'in', ['internal', 'transit'])])
        domain = ' sq.location_id in %s AND sq.quantity != 0 AND pp.active'
        args = (tuple(locations.ids),)

        vals = []
        Product = self.env['product.product']
        # Empty recordset of products available in stock_quants
        quant_products = self.env['product.product']

        # If inventory by company
        if self.company_id:
            domain += ' AND sq.company_id = %s'
            args += (self.company_id.id,)
        if self.product_ids:
            domain += ' AND sq.product_id in %s'
            args += (tuple(self.product_ids.ids),)

        self.env['stock.quant'].flush(['company_id', 'product_id', 'quantity', 'location_id', 'lot_id', 'package_id', 'owner_id'])
        self.env['product.product'].flush(['active'])
        self.env.cr.execute("""SELECT sq.product_id, sum(sq.quantity) as product_qty, sq.location_id, sq.lot_id as prod_lot_id, sq.package_id, sq.owner_id as partner_id
            FROM stock_quant sq
            LEFT JOIN product_product pp
            ON pp.id = sq.product_id
            WHERE %s
            GROUP BY sq.product_id, sq.location_id, sq.lot_id, sq.package_id, sq.owner_id """ % domain, args)

        product_exist = []
        for product_data in self.env.cr.dictfetchall():
            product_data['company_id'] = self.company_id.id
            product_data['inventory_id'] = self.id
            # replace the None the dictionary by False, because falsy values are tested later on
            for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                product_data[void_field] = False
            product_data['theoretical_qty'] = product_data['product_qty']
            if self.prefill_counted_quantity == 'zero':
                product_data['product_qty'] = 0
            if product_data['product_id']:
                product_data['product_uom_id'] = Product.browse(product_data['product_id']).uom_id.id
                quant_products |= Product.browse(product_data['product_id'])
            vals.append(product_data)
            product_exist.append(product_data['product_id'])

        if self.product_ids:
            product_ids = self.product_ids
        else:
            product_ids = Product.search([('type', '=', 'product')])

        for product_id in product_ids:
            if product_id.id not in product_exist:
                for location in locations:
                    vals.append({
                        'product_id' : product_id.id,
                        'product_qty' : 0,
                        'location_id' : location.id,
                        'prod_lot_id' : False,
                        'package_id' : False,
                        'partner_id' : False,
                        'company_id' : self.company_id.id,
                        'inventory_id' : self.id,
                        'theoretical_qty' : 0,
                        'product_uom_id' : product_id.uom_id.id,
                    })
        return vals

    def _action_start_show_all(self):
        """ Confirms the Inventory Adjustment and generates its inventory lines
        if its state is draft and don't have already inventory lines (can happen
        with demo data or tests).
        """
        for inventory in self:
            if inventory.state != 'draft':
                continue
            vals = {
                'state': 'confirm',
                'date': fields.Datetime.now()
            }
            if not inventory.line_ids and not inventory.start_empty:
                self.env['stock.inventory.line'].create(inventory._get_all_inventory_lines_values())
            inventory.write(vals)

    def action_start(self):
        if self.show_all:
            self.ensure_one()
            self._action_start_show_all()
            self._check_company()
            return self.action_open_inventory_lines()
        else:
            return super(stock_inventory, self).action_start()