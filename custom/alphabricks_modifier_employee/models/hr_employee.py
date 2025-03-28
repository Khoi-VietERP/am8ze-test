# -*- coding: utf-8 -*-

from odoo import models, fields, api


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    race_id = fields.Many2one('employee.race', string='Race')
    employee_address = fields.Char(string="Address")

class employee_race(models.Model):
    _name = 'employee.race'

    name = fields.Char(string='Name')
    rule_id = fields.Many2one('hr.salary.rule', string="Salary Rules")


