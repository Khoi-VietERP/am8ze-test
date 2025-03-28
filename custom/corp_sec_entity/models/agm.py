# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class entity_agm(models.Model):
    _name = 'entity.agm'

    fye_date = fields.Date('FYE Date')
    agm_date = fields.Date('AGM Date')
    agm_due_date = fields.Date('AGM Due Date')
    extension_175 = fields.Date('Extension S175')
    annual_return_date = fields.Date('Annual Return Date')
    annual_return_due_date = fields.Date('Annual return Due Date')
    extension_197 = fields.Date('Extension S197')
    last_agm_date = fields.Date('Last AGM Date')
    entity_agm_id = fields.Many2one('entity.agm')
    entity_id = fields.Many2one('corp.entity')

    def cover_date(self, date):
        date = date + relativedelta(years=1)
        date = datetime.date(date.year,date.month,date.day)
        return date.strftime(DEFAULT_SERVER_DATE_FORMAT)

    @api.model
    def create(self, vals_list):
        if vals_list.get('entity_agm_id',False):
            entity_agm_id = self.browse(vals_list.get('entity_agm_id',False))
            vals_list.update({
                'fye_date' : self.cover_date(entity_agm_id.fye_date),
                'agm_due_date' : self.cover_date(entity_agm_id.agm_due_date),
                'annual_return_due_date' : self.cover_date(entity_agm_id.annual_return_due_date),
                'last_agm_date' : self.cover_date(entity_agm_id.last_agm_date),
                'entity_id' : entity_agm_id.entity_id.id,
            })
            res = super(entity_agm, self).create(vals_list)
        else:
            res = super(entity_agm, self).create(vals_list)
            self.create({
                'entity_agm_id' : res.id
            })
        return res