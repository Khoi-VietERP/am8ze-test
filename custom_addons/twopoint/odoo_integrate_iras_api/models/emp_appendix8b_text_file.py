#  -*- encoding: utf-8 -*-

from odoo import fields, models, _

class binary_appendix8b_text_file_wizard(models.TransientModel):
    _inherit = 'binary.appendix8b.text.file.wizard'

    def submit_to_iras(self):
        for record in self:
            iras = self.env['iras.api.submit'].create({
                'filename': record.name,
                'file': record.appendix8b_txt_file,
                'api_type': 'submission_emp_income',
                'file_type': 'a8bInput',
            })
            self.env.cr.commit()
            return iras.send_submit()