# -*- coding: utf-8 -*-

from odoo import models, fields, api

class base_execute_query(models.TransientModel):
    _name = 'base.execute.query'

    query = fields.Text(string="Query")

    @api.model
    def execute_query(self, query, get_result=False):
        self.env.cr.execute(query)
        if get_result:
            results = self.env.cr.fetchall()
            return results
        return True

    def run_query(self):
        self.env.cr.execute(self.query)
