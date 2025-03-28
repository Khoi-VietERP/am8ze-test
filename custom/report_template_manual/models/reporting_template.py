from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ReportingTemplate(models.Model):
    _inherit = 'reporting.custom.template'

    is_manual_report = fields.Boolean()
    title_report = fields.Char('Title Report')
    report_id = fields.Many2one('ir.actions.report', copy= False)
    view_id = fields.Many2one('ir.ui.view', string='View')
    label_partner = fields.Char(string="Label Partner")
    field_id = fields.Many2one('ir.model.fields')
    name = fields.Char(required=False, string='Technical Name', compute="compute_name", store=True)
    signature_right = fields.Boolean('Signature On The Right')
    signature_right_text = fields.Char('Label Signature', default='Received By:')
    signature_left = fields.Boolean('Signature On The Left')
    signature_left_text = fields.Char('Label Signature', default='Checked / Approved / Authorised')
    report_partner_id = fields.Many2one('ir.model.fields', domain="[('model_id', '=', model_id), ('relation', '=', 'res.partner')]", string='Selected Partners')
    memo_id = fields.Many2one('ir.model.fields', domain="[('model_id', '=', model_id)]", string='Memo')

    def get_field_object(self, obj, field_id):
        return getattr(obj, field_id.name)

    def copy(self, default=None):
        if default is None:
            default = {}
        default['name_display'] = f"{self.name_display} (Copy)"
        return super(ReportingTemplate, self).copy(default)

    @api.onchange('field_id')
    def onchange_field_id(self):
        for rec in self:
            if rec.field_id:
                line_model_id = self.env['ir.model'].search([('model', '=', rec.field_id.relation)], limit=1)
                rec.line_model_id = line_model_id.id
    @api.depends('name_display')
    def compute_name(self):
        for rec in self:
            name = ''
            if rec.name_display:
                name = f'{rec.name_display.lower().strip().replace(" ", "_")}_{rec.id}'
            rec.name = name

    @api.constrains('name_display')
    def _check_name_display(self):
        for rec in self:
            if rec.name_display:
                exists = self.search([('name_display', '=', rec.name_display),('model_id', '=', rec.model_id.id), ('id', '!=', rec.id)])
                if exists:
                    raise ValidationError(_('This report name already exists.'))

    def action_general(self):
        self.ensure_one()

        if self.report_id:
            return

        paperformat_id = self.env['report.paperformat'].create({
            'name': f'{self.name_display} Manual A4',
            'default': True,
            'format': 'A4',
            'page_height': 0,
            'page_width': 0,
            'orientation': 'Portrait',
            'margin_top': 45,
            'margin_bottom': 28,
            'margin_left': 5,
            'margin_right': 5,
            'header_line': False,
            'header_spacing': 45,
            'dpi': 90,
        })
        actions_report_id = self.env['ir.actions.report'].create({
            'name': self.name_display,
            'model': self.model_id.model,
            'report_type': 'qweb-pdf',
            'report_name': f'custom_template.{self.name}',
            'print_report_name': f"'{self.name_display}'",
            'binding_model_id': self.model_id.id,
            'paperformat_id': paperformat_id.id,
            'binding_type': 'report'
        })
        view_arch = f"""<?xml version="1.0"?>
            <t t-name="{actions_report_id.report_name}">
                    <t t-call="web.html_container">
                        <t t-foreach="docs" t-as="o">
                            <t t-set="lang" t-value="o.company_id.partner_id.lang"/>
                            <t t-set="template" t-value="o.env['reporting.custom.template'].sudo().get_custom_template_id({self.id})"/>
                            <t>
                                <t t-call="report_template_manual.custom_template_report_document" t-lang="lang"/>
                            </t>
                        </t>
                    </t>
                </t>"""
        view_id = self.env['ir.ui.view'].create({
            'name': actions_report_id.report_name,
            'key': actions_report_id.report_name,
            'type': 'qweb',
            'arch': view_arch,
        })

        self.env['ir.model.data'].create({
            'name': self.name,
            'module': 'base',
            'model': view_id._name,
            'res_id': view_id.id,
        })
        header_company_field_ids = [(5, 0, 0),
                (0,0, {'prefix': False,'sequence': 1,'field_id': self.env.ref('base.field_res_company__street').id,}),
                (0,0, {'prefix': 'next_line','sequence': 2,'field_id': self.env.ref('base.field_res_company__street2').id,}),
                (0, 0, {'prefix': False, 'sequence': 3, 'field_id': self.env.ref('base.field_res_company__country_id').id, }),
                (0,0, {'prefix': False,'sequence': 4,'field_id': self.env.ref('base.field_res_company__zip').id,}),
                (0,0, {'prefix': 'next_line','sequence': 5,'field_id': self.env.ref(
                    'l10n_sg.field_res_company__l10n_sg_unique_entity_number').id, 'label': 'UEN'}),
                (0, 0, {'prefix': 'next_line', 'sequence': 6, 'field_id': self.env.ref(
                    'base.field_res_company__phone').id,'label': 'Tel'}),
                (0, 0, {'prefix': 'comma', 'sequence': 7, 'field_id': self.env.ref(
                    'base.field_res_company__email').id, 'label': 'Email'}),
            ]
        # partner_field_ids = [(5, 0, 0),
        #         (0,0, {'prefix': False,'sequence': 1,'field_id': self.env.ref('base.field_res_partner__street').id,}),
        #         (0,0, {'prefix': 'next_line','sequence': 2,'field_id': self.env.ref('base.field_res_partner__street2').id,}),
        #         (0,0, {'prefix': 'next_line','sequence': 3,'field_id': self.env.ref('base.field_res_partner__city').id,}),
        #         (0,0, {'prefix': 'comma','sequence': 4,'field_id': self.env.ref('base.field_res_partner__state_id').id,'field_display_field_id': self.env.ref('base.field_res_country_state__name').id}),
        #         (0,0, {'prefix': 'comma','sequence': 5,'field_id': self.env.ref('base.field_res_partner__zip').id,}),
        #         (0,0, {'prefix': 'next_line','sequence': 6,'field_id': self.env.ref('base.field_res_partner__country_id').id,'field_display_field_id': self.env.ref('base.field_res_country__name').id}),
        #     ]
        section_other_option_ids = [(5, 0, 0),
                (0,0, {'field_type': 'char', 'name_technical':'state_posted', 'name':'HEADING:IF STATE IS POSTED','value_char':''}),
                (0,0, {'field_type': 'char', 'name_technical':'state_draft', 'name':'HEADING:IF STATE IS DRAFT','value_char':''}),
                (0,0, {'field_type': 'char', 'name_technical':'state_cancel', 'name':'HEADING:IF STATE IS CANCELLED','value_char':''}),

                (0,0, {'field_type': 'boolean', 'name_technical':'show_serial_number', 'name':'Show serial number ?','value_boolean':True}),
                (0,0, {'field_type': 'char', 'name_technical':'serial_number_heading', 'name':'Serial number heading','value_char':'Sl.'}),

                (0,0, {'field_type': 'boolean', 'name_technical':'show_product_image', 'name':'Show product image ?','value_boolean':False}),
                (0,0, {'field_type': 'integer', 'name_technical':'product_image_position', 'name':'Product image position (Column)','value_integer':2}),
                (0,0, {'field_type': 'char', 'name_technical':'product_image_column_heading', 'name':'Product image heading','value_char':'Product Image'}),
                (0,0, {'field_type': 'char', 'name_technical':'product_image_width', 'name':'Product image width','value_char':'75px'}),

                (0,0, {'field_type': 'char', 'name_technical':'label_customer', 'name':'LABEL: Customer','value_char':'CUSTOMER'}),
                (0,0, {'field_type': 'char', 'name_technical':'label_communication_payment', 'name':'LABEL: Communication For Payment','value_char':''}),
                (0,0, {'field_type': 'char', 'name_technical':'multi_company_design_expression', 'name':'MULTI-COMPANY Design: Expression','value_char':''}),

                (0,0, {'field_type': 'integer', 'name_technical':'padding_after_header', 'name':'Padding After Header (Px)','value_integer':24}),
                (0,0, {'field_type': 'boolean', 'name_technical':'footer_single_line', 'name':'Single Line Footer','value_boolean':False}),

            ]
        self.write({
            'header_company_field_ids': header_company_field_ids,
            'visible_partner_section': True,
            # 'partner_field_ids': partner_field_ids,
            'visible_section_2': True,
            'visible_section_lines': True,
            'visible_section_footer': True,
            'visible_watermark': True,
            'amount_in_text_visible': True,
            'section_other_option_ids': section_other_option_ids,
            'report_id':actions_report_id.id,
            'view_id':view_id.id,
            'paperformat_id':paperformat_id.id,
        })

    def get_custom_template_id(self, record):
        return self.browse(record)

    def action_preview_custom(self):
        model_id = self.env[self.model_id.model].search([], limit=1)

        if not model_id:
            raise ValidationError(_(f'Not found any {self.model_id.name} for template. Please create any one!'))
        url = f"report/pdf/{self.report_id.report_name}/{model_id.id}"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }


    def unlink(self):
        for rec in self:
            if rec.report_id:
                rec.report_id.paperformat_id.unlink()
                rec.report_id.unlink()
                rec.view_id.unlink()
        return super(ReportingTemplate, self).unlink()

    def get_o2m_data(self, obj, o2m_field_id_name):
        self.ensure_one()

        vals = []
        for line in getattr(self, o2m_field_id_name).sorted(key=lambda r: r.sequence):
            if not line.field_id:
                continue

            thousands_separator = hasattr(line, 'thousands_separator') and line.thousands_separator or False
            value = self.get_field_data(obj=obj, field_id=line.field_id, display_field=line.field_display_field_id.name, thousands_separator=thousands_separator)

            if o2m_field_id_name == 'section_footer_field_ids':
                vals.append({
                    'label': line.label and line.label.strip() or line.field_id.field_description,
                    'value': value,
                    'tax_group': line.tax_group or False,
                    'null_value_display': hasattr(line, 'null_value_display') and line.null_value_display or False
                })
            else:
                vals.append({
                    'label': line.label and line.label.strip() or line.field_id.field_description,
                    'value': value,
                    'null_value_display': hasattr(line, 'null_value_display') and line.null_value_display or False
                })
        return vals
