# -*- coding: utf-8 -*-

from odoo import models, fields, api


class wms_distance_from(models.Model):
    _name = 'wms.distance.from'
    _description = 'WMS Distance From'

    distance_id = fields.Many2one('wms.distance', 'Distance')
    location_id = fields.Many2one('stock.location', 'Location')
    to_ids = fields.One2many('wms.distance.to', 'from_id', 'Locations to')
