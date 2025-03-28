# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class HrExpense(models.Model):

	_inherit = "hr.expense"
	

	merchant_id = fields.Many2one("res.partner", string="Merchant")
	project_id = fields.Many2one("project.project", string="Project")
