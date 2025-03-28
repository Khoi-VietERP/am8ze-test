# -*- coding: utf-8 -*-

from odoo import models, fields, api


class wms_distance_to(models.Model):
    _name = 'wms.distance.to'
    _description = 'WMS Distance To'

    from_id = fields.Many2one('wms.distance.from', 'From')
    location_id = fields.Many2one('stock.location', 'Location')
    distance = fields.Float('Distance', default=0)
