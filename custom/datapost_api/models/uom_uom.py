from odoo import models, fields


class UomUom(models.Model):
    _inherit = 'uom.uom'

    peppol_code = fields.Char('Peppol Code')
