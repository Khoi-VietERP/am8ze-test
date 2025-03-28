# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ACSMultiDocument(models.TransientModel):
    _name = "acs.multi.document"
    _description = "Upload Multiple Documents"

    directory_id = fields.Many2one('document.directory', "Directory")
    document_ids = fields.Many2many('ir.attachment', 'multi_attachment_rel', 'multi_id',
                                      'attachment_id', 'Documents',
                                      help="Select multiple files to upload.")

    def create_documents(self):
        for rec in self:
            directory = False
            if rec.directory_id:
                directory = rec.directory_id.id          
            for attach in rec.document_ids:
                self.env['document.document'].create({
                    'name': attach.name,
                    'document': attach.datas,
                    'directory_id': directory,
                    })
        view_id = self.env.ref('document_management.view_document_document_kanban').id
        return {
            'name': _('Documents'),
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban',
            'res_model': 'document.document',
            'view_id': view_id,
        }