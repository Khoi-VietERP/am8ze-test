# -*- coding: utf-8 -*-

from odoo import models, fields, api


class product_template_ihr(models.Model):
    _inherit = 'product.template'

    default_code = fields.Char('Product Code')

    def action_edit_description_sale(self):
        action = self.env.ref('alphabricks_modifier_product.action_edit_description_sale').read()[0]
        action['context'] = {
            'default_product_tmpl_id' : self.id,
            'default_description_sale' : self.description_sale
        }
        return action

    def open_product_form(self):
        action = self.env.ref('stock.product_template_action_product').read()[0]
        res = self.env.ref('product.product_template_only_form_view', False)
        form_view = [(res and res.id or False, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.id
        return action

class edit_description_sale(models.TransientModel):
    _name = "edit.description.sale"

    description_sale = fields.Text('Sales Description')
    product_tmpl_id = fields.Many2one('product.template')

    def action_save(self):
        if self.product_tmpl_id:
            self.product_tmpl_id.description_sale = self.description_sale

class product_product(models.Model):
    _inherit = "product.product"

    def get_product_multiline_description_sale(self):
        """ Compute a multiline description of this product, in the context of sales
                (do not use for purchases or other display reasons that don't intend to use "description_sale").
            It will often be used as the default description of a sale order line referencing this product.
        """
        name = self.display_name
        if self.description_sale:
            name = self.description_sale

        return name


