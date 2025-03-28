# -*- coding: utf-8 -*-

from odoo import models, fields, api


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    def unlink(self):
        for rec in self:
            rec.history_ids.unlink()
        return super(hr_employee, self).unlink()
