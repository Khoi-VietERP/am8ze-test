
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class IrModel(models.Model):
    _inherit = 'ir.model'


    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        model_id = self._context.get('search_line_model')
        if model_id:
            fields_ids = self.env['ir.model.fields'].search([('model_id', '=', model_id),('ttype', 'in', ['one2many', 'many2many'])])
            relation_list = fields_ids.mapped('relation')
            args += [('model', 'in', relation_list)]
        return super(IrModel, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)