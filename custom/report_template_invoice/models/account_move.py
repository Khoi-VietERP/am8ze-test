# -*- coding: utf-8 -*-
import ast
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_customer_invoice_template_id(self):
        self.ensure_one()
        if self.type != 'out_invoice':
            return False
        return self.env['reporting.custom.template'].sudo().get_template('report_customer_invoice')


class ReportingTemplate(models.Model):
    _inherit = 'reporting.custom.template'

    template_note = fields.Text(string="Note")
    show_paynow_qr = fields.Boolean(string="Show Paynow QR")
    margin_top_header = fields.Char(string="Margin Top Header")
    margin_bottom_header = fields.Char(string="Margin Bottom Header")
    margin_left_header = fields.Char(string="Margin Left Header")
    margin_right_header = fields.Char(string="Margin Right Header")

    def get_colors(self, company_id=False):
        self.ensure_one()
        colors = super(ReportingTemplate, self).get_colors()

        multi_company_expression = self.get_other_option_data('multi_company_design_expression')

        if company_id and multi_company_expression:

            try:
                value = ast.literal_eval(multi_company_expression)
            except:
                value = False

            if value and type(value) == dict:
                value = value.get(company_id.id)
                if value:
                    template = self.env['reporting.custom.template.template'].search([
                        ('report_name', '=', self.name),
                        ('name', '=', value),
                    ])

                    if template:
                        colors.color1 = template.color1
                        colors.color2 = template.color2
                        colors.color3 = template.color3
        return colors


    def get_template_note(self, record=False):
        self.ensure_one()
        template_note = self.template_note
        if record:
            template_note_render = self.env['mail.template']._render_template(template_note, record._name, record.ids)
            template_note = template_note_render.get(record.id)
        return template_note


    def action_preview(self):
        move_id = self.env['account.move'].search([('type', '=', 'out_invoice'), ('state', '=', 'posted')], limit=1)
        if not move_id:
            move_id = self.env['account.move'].search([('type', '=', 'out_invoice')], limit=1)

        if not move_id:
            raise ValidationError(_('Not found any invoice for template. Please create any one!'))
        action = move_id.preview_invoice()
        action.update({
            'target' : 'new'
        })

        return action
