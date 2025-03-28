# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProjectType(models.Model):
    _name = 'project.type'

    name = fields.Char('Project Type', size=256)

class DesignType(models.Model):
    _name = 'design.type'

    name = fields.Char('Design Type', size=256)

class SupplierType(models.Model):
    _name = 'supplier.type'

    name = fields.Char('Supplier Type', size=256)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_type_id = fields.Many2one('project.type', 'Project Types')
    design_type_id = fields.Many2one('design.type', 'Design Types')
    supplier_type_id = fields.Many2one('supplier.type', 'Supplier Types')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        if self.project_type_id:
            result.update({'project_type_id': self.project_type_id.id})
        if self.design_type_id:
            result.update({'design_type_id': self.design_type_id.id})
        if self.supplier_type_id:
            result.update({'supplier_type_id': self.supplier_type_id.id})
        return result

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        for rc in self:
            rc.write({'name': self.env['ir.sequence'].next_by_code('sale.order.validated')})
        return result


    project_type_id = fields.Many2one('project.type', 'Project Types')
    design_type_id = fields.Many2one('design.type', 'Design Types')
    supplier_type_id = fields.Many2one('supplier.type', 'Supplier Types')

class Invoice(models.Model):
    _inherit = 'account.move'

    project_type_id = fields.Many2one('project.type', 'Project Types')
    design_type_id = fields.Many2one('design.type', 'Design Types')
    supplier_type_id = fields.Many2one('supplier.type', 'Supplier Types')
