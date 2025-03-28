# -*- coding: utf-8 -*-

from odoo import models, fields, api

amount_python_compute = """
if not employee.singaporean and employee.pr_year == 1:
    if employee.age >= 66:
        if categories.BASIC > 500 and categories.BASIC < 750:
            result =  math.floor((categories.BASIC - 500) * 0.15)
        elif categories.BASIC >= 750:
            if ow_total > 6000:
                result =  math.floor((6000 * 0.05) + (aw_total * 0.05))
            else:
                result =  math.floor(categories.BASIC * 0.05)
        else:
            result=0
    elif employee.age >= 61 and employee.age <=65:
        if categories.BASIC > 500 and categories.BASIC < 750:
            result =  math.floor((categories.BASIC - 500) * 0.15)
        elif categories.BASIC >= 750:
            if ow_total > 6000:
                result =  math.floor((6000 * 0.05) + (aw_total * 0.05))
            else:
                result =  math.floor(categories.BASIC * 0.05)
        else:
            result=0
    elif employee.age >= 56 and employee.age <=60:
        if categories.BASIC > 500 and categories.BASIC < 750:
            result =  math.floor((categories.BASIC - 500) * 0.15)
        elif categories.BASIC >= 750:
            if ow_total > 6000:
                result =  math.floor((6000 * 0.05) + (aw_total * 0.05))
            else:
                result =  math.floor(categories.BASIC * 0.05)
        else:
            result=0
    elif employee.age <=55:
        if categories.BASIC > 500 and categories.BASIC < 750:
            result =  math.floor((categories.BASIC - 500) * 0.15)
        elif categories.BASIC >= 750:
            if ow_total > 6000:
                result =  math.floor((6000 * 0.05) + (aw_total * 0.05))
            else:
                result =  math.floor(categories.BASIC * 0.05)
        else:
            result=0
elif not employee.singaporean and employee.pr_year == 2:
    if employee.age >= 66:
        if categories.BASIC > 500 and categories.BASIC < 750:
            result =  math.floor((categories.BASIC - 500) * 0.15)
        elif categories.BASIC >= 750:
            if ow_total > 6000:
                result =  math.floor((6000 * 0.05) + (aw_total * 0.05))
            else:
                result =  math.floor(categories.BASIC * 0.05)
        else:
            result=0
    elif employee.age >= 61 and employee.age <=65:
        if categories.BASIC > 500 and categories.BASIC < 750:
            result =  math.floor((categories.BASIC - 500) * 0.225)
        elif categories.BASIC >= 750:
            if ow_total > 6000:
                result =  math.floor((6000 * 0.075) + (aw_total * 0.075))
            else:
                result =  math.floor(categories.BASIC * 0.075)
        else:
            result=0
    elif employee.age >= 56 and employee.age <=60:
        if categories.BASIC > 500 and categories.BASIC < 750:
            result =  math.floor((categories.BASIC - 500) * 0.375)
        elif categories.BASIC >= 750:
            if ow_total > 6000:
                result =  math.floor((6000 * 0.125) + (aw_total * 0.125))
            else:
                result =  math.floor(categories.BASIC * 0.125)
        else:
            result=0
    elif employee.age <=55:
        if categories.BASIC > 500 and categories.BASIC < 750:
            result =  math.floor((categories.BASIC - 500) * 0.45)
        elif categories.BASIC >= 750:
            if ow_total > 6000:
                result =  math.floor((6000 * 0.15) + (aw_total * 0.15))
            else:
                result = math.floor(categories.BASIC * 0.15)
        else:
            result=0
elif employee.singaporean or employee.pr_year >= 3:
    if employee.age > 70:
        if categories.BASIC > 500.01 and categories.BASIC <= 750:
            result = math.floor((categories.BASIC - 500) * 0.15)
        elif categories.BASIC > 750:
            if categories.BASIC > 6000:
                result = math.floor(6000 * 0.05)
            else:
                result = math.floor(categories.BASIC * 0.05)
        else:
            result = 0
    elif employee.age >= 66 and employee.age <= 70:
        if categories.BASIC > 500.01 and categories.BASIC <= 750:
            result = math.floor((categories.BASIC - 500) * 0.21)
        elif categories.BASIC > 750:
            if categories.BASIC > 6000:
                result = math.floor(6000 * 0.07)
            else:
                result = math.floor(categories.BASIC * 0.07)
        else:
            result = 0
    elif employee.age >= 61 and employee.age <= 65:
        if categories.BASIC > 500.01 and categories.BASIC <= 750:
            result = math.floor((categories.BASIC - 500) * 0.285)
        elif categories.BASIC > 750:
            if categories.BASIC > 6000:
                result = math.floor(6000 * 0.095)
            else:
                result = math.floor(categories.BASIC * 0.095)
        else:
            result = 0
    elif employee.age >= 56 and employee.age <= 60:
        if categories.BASIC > 500.01 and categories.BASIC <= 750:
            result = math.floor((categories.BASIC - 500) * 0.45)
        elif categories.BASIC > 750:
            if categories.BASIC > 6000:
                result = math.floor(6000 * 0.15)
            else:
                result = math.floor(categories.BASIC * 0.15)
        else:
            result = 0
    elif employee.age <= 55:
        if categories.BASIC > 500.01 and categories.BASIC <= 750:
            result = math.floor((categories.BASIC - 500) * 0.6)
        elif categories.BASIC > 750:
            if categories.BASIC > 6000:
                result = math.floor(6000 * 0.20)
            else:
                result = math.floor(categories.BASIC * 0.20)
        else:
            result = 0
else:
    result=0"""

rule_list = ['CPFEE_SPR_SIN', 'CPFTOTAL_SPR_SIN', 'CPFER_SPR_SIN','NET','CPFCDAC','CPFSDL']

class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'

    @api.model
    def update_amount_python_compute(self):
        salary_rule_ids = self.search([('code', 'in', rule_list)])
        for salary_rule_id in salary_rule_ids:
            salary_rule_id.condition_python = salary_rule_id.condition_python.replace('GROSS','BASIC')
            salary_rule_id.amount_python_compute = salary_rule_id.amount_python_compute.replace('GROSS','BASIC')

        salary_rule_id = self.search([('name', '=', 'CPF Employee'),('code', '=', 'CPFEE_SPR_SIN')])
        salary_rule_id.amount_python_compute = amount_python_compute


