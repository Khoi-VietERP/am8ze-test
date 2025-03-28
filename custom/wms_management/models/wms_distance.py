# -*- coding: utf-8 -*-

from odoo import models, fields, api


class wms_distance(models.Model):
    _name = 'wms.distance'
    _description = 'WMS Distance'

    name = fields.Char('Name')
    from_ids = fields.One2many('wms.distance.from', 'distance_id', 'From')

    def action_load(self):
        locations = self.env['stock.location'].search([
            ('usage', '=', 'internal'),
        ])
        for record in self:
            for from_location in locations:
                location_from = record.from_ids.create({
                    'distance_id': record.id,
                    'location_id': from_location.id,
                })
                for to_location in locations:
                    location_from.to_ids.create({
                        'from_id': location_from.id,
                        'location_id': to_location.id,
                    })


