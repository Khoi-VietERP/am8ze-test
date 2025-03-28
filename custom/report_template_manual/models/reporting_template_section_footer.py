# -*- coding: utf-8 -*-
from odoo import models, fields


class ReportingTemplateSectionFooter(models.Model):
    _inherit = 'reporting.custom.template.section.footer'

    tax_group = fields.Boolean('Tax Group')


