# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.tools.mimetypes import guess_mimetype
import mimetypes


class DocumentDocument(models.Model):
    _description = 'Document'
    _name = "document.document"
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    document = fields.Binary("Document", attachment=True)
    directory_id = fields.Many2one('document.directory', string='Directory')
    description = fields.Html(string='Description')
    tag_ids = fields.Many2many('document.tag', 'acs_document_tag_rel', 'document_id', 'tag_id', 
        string='Tags', help="Classify and analyze your Document")
    mimetype = fields.Char('Mime Type', readonly=True)

    revision_no = fields.Integer('Revision No', readonly=True, default=1)
    parent_document_id = fields.Many2one('document.document', string='Parent Document')
    revised_document_id = fields.Many2one('document.document', string='Revised Document')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.company)

    def _check_contents(self, values):
        mimetype = None
        if values.get('mimetype'):
            mimetype = values['mimetype']
        if not mimetype and values.get('name'):
            mimetype = mimetypes.guess_type(values['name'])[0]
        if not mimetype and values.get('url'):
            mimetype = mimetypes.guess_type(values['url'])[0]
        if values.get('datas') and (not mimetype or mimetype == 'application/octet-stream'):
            mimetype = guess_mimetype(values['datas'].decode('base64'))
        if not mimetype:
            mimetype = 'application/octet-stream'

        values['mimetype'] = mimetype
        xml_like = 'ht' in mimetype or 'xml' in mimetype # hta, html, xhtml, etc.
        force_text = (xml_like and (not self.env.user._is_admin() or
            self.env.context.get('attachments_mime_plainxml')))
        if force_text:
            values['mimetype'] = 'text/plain'
        return values

    def revise_document(self):
        action = self.env.ref('document_management.action_document_document').read()[0]
        action['views'] = [(self.env.ref('document_management.view_document_document_form').id, 'form')]
        action['context'] = {
            'default_revision_no': self.revision_no+1,
            'default_directory_id': self.directory_id and self.directory_id.id or False,
            'default_parent_document_id': self.id,
        }
        return action 

    @api.model
    def create(self, values):
        values = self._check_contents(values)
        res = super(DocumentDocument, self).create(values)
        if res.parent_document_id:
            res.parent_document_id.revised_document_id = res.id
        return res

    def write(self, vals):
        if 'mimetype' in vals or 'document' in vals:
            vals = self._check_contents(vals)
        return super(DocumentDocument, self).write(vals)

    def action_document_send(self):
        '''
        This function opens a window to compose an email, with the template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('document_management', 'acs_document_email')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False


        attachment = self.env['ir.attachment'].create({
            'name': self.name,
            'datas': self.document,
            'res_model': 'document.document',
            'res_id': self.id,
        })

        ctx = {
            'default_model': 'document.document',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_attachment_ids': [(6, 0, [attachment.id])],
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class DocumentDirectory(models.Model):
    _description = 'Document Directory'
    _name = "document.directory"
    _inherit = ['mail.thread','mail.activity.mixin']

    def _get_document_count(self):
        res = {}
        DocumentObj = self.env['document.document']
        for dir in self:
            dir.document_count = len(dir.document_ids) or 0

    name = fields.Char(required=True)
    parent_id = fields.Many2one('document.directory',string='Parent Directory', index=True)
    children_ids = fields.One2many('document.directory', 'parent_id', string='Children', copy=True)
    user_ids = fields.Many2many('res.users', 'document_user_rel', 'user_id', 'doc_id', string="Users")
    document_count = fields.Integer(compute='_get_document_count', string="Number of documents attached")
    description = fields.Html(string='Description')
    document_ids = fields.One2many(comodel_name='document.document', inverse_name='directory_id', string='Documents')
    tag_ids = fields.Many2many('document.tag', 'directory_tag_rel', 'directory_id', 'tag_id', 
        string='Tags', help="Classify and analyze your Document")
    department_id = fields.Many2one('hr.department', string='Department')
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.company)


    def name_get(self):
        def get_names(directory):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            res = []
            while directory:
                res.append(directory.name)
                directory = directory.parent_id
            return res
        return [(directory.id, " / ".join(reversed(get_names(directory)))) for directory in self]

    @api.constrains('parent_id')
    def _check_directory_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive Directory.'))
        return True


class Tag(models.Model):

    _name = "document.tag"
    _description = "Document Tags"

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: