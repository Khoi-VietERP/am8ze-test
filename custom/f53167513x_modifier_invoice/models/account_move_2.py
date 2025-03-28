# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from lxml import etree

class account_move_2(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection_add=[('void', 'Void')])

    @api.model
    def create(self, values):
        result = super(account_move_2, self).create(values)
        return result

    def action_void_invoice(self):
        active_ids = self.env.context.get('active_ids')
        move_ids = self.env['account.move'].browse(active_ids)
        for move_id in move_ids:
            if move_id.state == 'posted':
                raise UserError(_("You cannot delete an entry which has been posted once."))
            move_id.line_ids.unlink()
            move_id.state = 'void'

    def write(self, vals):
        res = super(account_move_2, self).write(vals)
        state = vals.get('state', False)
        if state and state != 'void':
            for rec in self:
                if rec.state == 'void':
                    type = dict(rec.fields_get(['type'])['type']['selection']).get(rec.type, '')
                    raise UserError(_("You cannot edit void %s!" % type))
        return res