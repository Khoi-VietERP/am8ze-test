# -*- coding: utf-8 -*-

import json

from lxml import etree
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        ret_val = super(ResConfigSettings, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

        doc = etree.XML(ret_val['arch'])

        for node in doc.xpath("//field[@widget='upgrade_boolean']"):
            node.set("readonly", "1")
            node.set("invisible", "1")
            node.set("widget", "")
            modifiers = json.loads(node.get("modifiers"))
            modifiers['readonly'] = True
            modifiers['invisible'] = True
            node.set("modifiers", json.dumps(modifiers))

        ret_val['arch'] = etree.tostring(doc, encoding='unicode')
        return ret_val