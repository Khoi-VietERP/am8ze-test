# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner'

    name_au_officer = fields.Char('Name of the Authorised Officer')
    officical_designation = fields.Char('Official Designation')
    uen = fields.Char('UEN')
    date_of_activation = fields.Date('Date of activation')
    receive_update = fields.Boolean('Receive update or news from Portal')
    date_of_payment = fields.Date('Date of Payment for membership fees')
    expire_date = fields.Date('Expire Date of Membership')
    payment_mode = fields.Char('Payment mode')
    remarks = fields.Text('Comment/Remarks')
    referred_by = fields.Many2one('res.users', 'Referred by')
    approved_by = fields.Many2one('res.users', 'Approved by')
    snippet_ids = fields.Many2many('seller.snippets')
    snippet_lines = fields.One2many('seller.snippets.line', 'partner_id')

    staff_strength_id = fields.Many2one('staff.strength', 'Staff Strength')
    industry_sector_id = fields.Many2one('industry.sector', 'Industry Sector')
    personal_email_address = fields.Char('Personal Email Address')
    date_of_signing = fields.Date('Date of signing up the membership')

class staff_strength(models.Model):
    _name = 'staff.strength'

    name = fields.Char('Name')


class seller_snippets_line(models.Model):
    _name = 'seller.snippets.line'

    snippet_id = fields.Many2one('seller.snippets', required=1)
    code = fields.Char('Code')
    type = fields.Selection([
        ('structure', 'Structure'),
        ('features', 'Features'),
        ('effects', 'Effects'),
        ('inner_content', 'Inner content'),
    ], related='snippet_id.type')
    partner_id = fields.Many2one('res.partner')

    img_attach = fields.Html('Image', compute="_get_img_html")

    def _get_img_html(self):
        for elem in self:
            elem.img_attach = '<img src="%s"/>' % elem.snippet_id.image_url

    def create_template_snippet(self):
        snippet_template_id = self.env.ref(self.snippet_id.code)
        if snippet_template_id:
            name = snippet_template_id.name + " " + str(self.id)
            key = snippet_template_id.key + str(self.id)

            model_data_id = snippet_template_id.model_data_id.sudo().copy(
                dict(module="website", name=key.split('.')[1], display_name=name))
            new_snippet_template_id = snippet_template_id.sudo().copy(dict(name=name, key=key, model_data_id=model_data_id.id))
            model_data_id.sudo().res_id = new_snippet_template_id.id
            self.code = key

    def remove_template_snippet(self):
        for rec in self:
            view_ids = self.env['ir.ui.view'].sudo().search([('key', '=', rec.code)])
            view_ids.sudo().unlink()

    @api.model
    def create(self, vals):
        res = super(seller_snippets_line, self).create(vals)
        res.create_template_snippet()
        return res

    def write(self, vals):
        if vals.get('snippet_id'):
            self.remove_template_snippet()
        res = super(seller_snippets_line, self).write(vals)
        if vals.get('snippet_id'):
            for rec in self:
                rec.create_template_snippet()
        return res

    def unlink(self):
        self.remove_template_snippet()
        return super(seller_snippets_line, self).unlink()


class seller_snippets(models.Model):
    _name = 'seller.snippets'

    type = fields.Selection([
        ('structure','Structure'),
        ('features','Features'),
        ('effects','Effects'),
        ('inner_content','Inner content'),
    ])
    name = fields.Char('Name')
    code = fields.Char('Code', required=1)
    image_url = fields.Char('Image')
    img_attach = fields.Html('Image', compute="_get_img_html")

    def _get_img_html(self):
        for elem in self:
            elem.img_attach = '<img src="%s"/>' % elem.image_url


