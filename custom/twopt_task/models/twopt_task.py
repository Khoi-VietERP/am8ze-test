# -*- coding: utf-8 -*-

from odoo import models, fields, api

class task_filing(models.TransientModel):
    _name = 'task.filing'

    name = fields.Char('Name', default='Task Filing')

class task_non_filing(models.Model):
    _name = 'task.non.filing'

    name = fields.Char('Name', default='Task Non Filing')
