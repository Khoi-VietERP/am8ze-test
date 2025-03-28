#  -*- encoding: utf-8 -*-

from odoo import fields, models, _

class binary_ir8s_text_file_wizard(models.TransientModel):
    _inherit = 'binary.ir8s.text.file.wizard'

    def submit_to_iras(self):
        for record in self:
            iras = self.env['iras.api.submit'].create({
                'filename': record.name,
                'file': record.ir8s_txt_file,
                'api_type': 'submission_emp_income',
                'file_type': 'ir8sInput',
            })
            self.env.cr.commit()
            return iras.send_submit()