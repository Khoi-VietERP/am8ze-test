# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from lxml import etree
import json

class BaseModel(models.AbstractModel):
    _inherit = 'base'

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(BaseModel, self).fields_view_get(
    #         view_id=view_id, view_type=view_type,
    #         toolbar=toolbar, submenu=submenu)
    #
    #     date_lock = self.env['ir.config_parameter'].get_param('h202_access_date_lock.date_lock')
    #     model = res.get('model', False)
    #     if date_lock and model != 'res.config.settings':
    #         date_lock = datetime.strptime(date_lock, DATE_FORMAT).date()
    #         today = datetime.now().date()
    #         if date_lock < today:
    #             if view_type == 'kanban':
    #                 doc = etree.XML(res['arch'])
    #                 for node in doc.xpath("//kanban"):
    #                     node.set("create", "false")
    #                     node.set("delete", "false")
    #                     node.set("edit", "false")
    #
    #                 for node in doc.xpath("//button"):
    #                     node.set("invisible", "1")
    #                     modifiers = json.loads(node.get("modifiers") or '{}')
    #                     modifiers['invisible'] = True
    #                     node.set("modifiers", json.dumps(modifiers))
    #
    #                 res['arch'] = etree.tostring(doc, encoding='unicode')
    #             if view_type == 'activity':
    #                 doc = etree.XML(res['arch'])
    #                 for node in doc.xpath("//activity"):
    #                     node.set("class", node.get('class',"") + " lock_form_view")
    #
    #                 res['arch'] = etree.tostring(doc, encoding='unicode')
    #             if view_type == 'calendar':
    #                 doc = etree.XML(res['arch'])
    #                 for node in doc.xpath("//calendar"):
    #                     node.set("class", node.get('class',"") + " lock_form_view")
    #
    #                 res['arch'] = etree.tostring(doc, encoding='unicode')
    #             if view_type == 'tree':
    #                 doc = etree.XML(res['arch'])
    #                 for node in doc.xpath("//tree"):
    #                     node.set("create", "false")
    #                     node.set("delete", "false")
    #                     node.set("edit", "false")
    #
    #                 for node in doc.xpath("//button"):
    #                     node.set("invisible", "1")
    #                     modifiers = json.loads(node.get("modifiers") or '{}')
    #                     modifiers['invisible'] = True
    #                     node.set("modifiers", json.dumps(modifiers))
    #
    #                 res['arch'] = etree.tostring(doc, encoding='unicode')
    #
    #                 toolbar_dict = res.get("toolbar", {})
    #                 toolbar_dict["action"] = []
    #                 res["toolbar"] = toolbar_dict
    #             if view_type == 'form':
    #                 doc = etree.XML(res['arch'])
    #                 for node in doc.xpath("//form"):
    #                     node.set("create", "false")
    #                     node.set("delete", "false")
    #                     node.set("edit", "false")
    #                     node.set("class", node.get('class',"") + " lock_form_view")
    #
    #                 for node in doc.xpath("//button"):
    #                     node.set("invisible", "1")
    #                     modifiers = json.loads(node.get("modifiers") or '{}')
    #                     modifiers['invisible'] = True
    #                     node.set("modifiers", json.dumps(modifiers))
    #
    #                 res['arch'] = etree.tostring(doc, encoding='unicode')
    #
    #                 toolbar_dict = res.get("toolbar", {})
    #                 toolbar_dict["action"] = []
    #                 res["toolbar"] = toolbar_dict
    #
    #     return res
