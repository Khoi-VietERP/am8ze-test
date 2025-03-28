#  -*- encoding: utf-8 -*-

from odoo import fields, models, _

class BinaryAppendix8aTextFileWizard(models.TransientModel):
    _inherit = 'binary.appendix8a.text.file.wizard'

    def submit_to_iras(self):
        for record in self:
            iras = self.env['iras.api.submit'].create({
                'filename': record.name,
                'file': record.appendix8a_txt_file,
                'api_type': 'submission_emp_income',
                'file_type': 'a8aInput',
            })
            self.env.cr.commit()
            return iras.send_submit()