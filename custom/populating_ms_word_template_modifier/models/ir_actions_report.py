# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from mailmerge import MailMerge
from lxml import etree
import binascii
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from datetime import datetime,date
import logging
import pytz


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    ms_model_id = fields.Many2one('ir.model', string="Model Name", domain=[('transient', '!=', True)])
    ms_model_select = fields.Selection([
        ('sale.order', 'Sale'),
        ('purchase.order', 'Purchase'),
        ('account.move', 'Invoice'),
        ('res.partner', 'Partner'),
        ('stock.picking', 'Inventory'),
    ], string="Model Name")

    @api.onchange('ms_model_id')
    def onchange_ms_model(self):
        self.model = self.ms_model_id.model

    @api.onchange('ms_model_select')
    def onchange_ms_select_model(self):
        self.model = self.ms_model_select