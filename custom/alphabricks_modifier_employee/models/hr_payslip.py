from odoo import _, api, fields, models

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        """Compute sheet."""
        result = super(HrPayslip, self).compute_sheet()
        lines = []
        for payslip in self:
            for line in payslip.line_ids:
                if line.category_id.code == 'CATCPFAGENCYSERVICESEE' and line.employee_id.race_id.rule_id != line.salary_rule_id:
                    lines.append(line.id)
        if lines:
            line_rec = self.env['hr.payslip.line'].browse(lines)
            line_rec.unlink()
        return result