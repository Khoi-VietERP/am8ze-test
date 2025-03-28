# -*- coding: utf-8 -*-

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

import base64
from io import BytesIO
from odoo import models, fields, api

class COWizard(models.TransientModel):
    _name = 'co.wizard'

    name = fields.Char('Report Name', default='CO Report')
    select_co = fields.Boolean('Select CO', default=True)
    select_field = fields.Boolean('Select Field', default=True)

    def print_excel(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Export Overview')

        header_style = workbook.add_format({
            'bold': False,
            'italic': True,
            'font_size': '12',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })


        text_style = workbook.add_format({
            'bold': True,
            'italic': False,
            'font_size': '12',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        number_style = workbook.add_format({
            'bold': True,
            'italic': False,
            'font_size': '12',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
        })
        number_style.set_num_format('#,##0')

        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:M', 25)

        summary_header = [
            'Case No.',
            'Name of Client',
            'Name of Debtor',
            'Total Amount Due',
            'Amount Claim by Client',
            'DAA Charges',
            'DAA Commission',
            'Visitation Fee No.',
            'Visitation Fee',
            'Final Amount due to Client',
            'Total DAA Profit',
            'Sales In Charge',
        ]
        row = 0
        [worksheet.write(row, header_cell, summary_header[header_cell], header_style) for header_cell in range(0, len(summary_header)) if summary_header[header_cell]]

        case_ids = self.env.context.get('active_ids', [])
        for case in self.env['daa.case'].browse(case_ids):
            row += 1

            no_of_visitations = len(case.visitation_ids)
            visitation_fee = no_of_visitations * 30
            commission = case.assigned_amount * 0.3
            daa_charges = case.total_amount - case.assigned_amount - visitation_fee
            final_amount = case.assigned_amount * 0.7
            total_profit = case.total_amount - final_amount - commission - visitation_fee

            worksheet.write(row, 0, case.id, text_style)
            worksheet.write(row, 1, case.client_id.name or '', text_style)
            worksheet.write(row, 2, case.debtor_id.name or '', text_style)

            worksheet.write(row, 3, case.total_amount or '', number_style)
            worksheet.write(row, 4, case.assigned_amount or '', number_style)
            worksheet.write(row, 5, daa_charges or '', number_style)
            worksheet.write(row, 6, commission or '', number_style)
            worksheet.write(row, 7, no_of_visitations or '', number_style)
            worksheet.write(row, 8, visitation_fee or '', number_style)
            worksheet.write(row, 9, final_amount or '', number_style)
            worksheet.write(row, 10, total_profit or '', number_style)
            worksheet.write(row, 11, case.agreement_id.saleperson_id.name or '', text_style)

        row += 3
        worksheet.write(row, 0, 'No of Officer:', text_style)
        worksheet.write(row, 1, '3', number_style)
        field_officers = [
            'Field Officer 1:',
            'Field Officer 2:',
            'Field Officer 3:',
            'Field Officer 4:',
            'Field Officer 5:',
            'Field Officer 6:',
            'Field Officer 7:',
            'Field Officer 8:',
            'Field Officer 9:',
            'Field Officer 10:',
        ]
        for field_officer in field_officers:
            row += 1

            worksheet.write(row, 0, field_officer, text_style)
            worksheet.write(row, 1, '', number_style)

        row += 2
        payment_header = [
            'Payment Date',
            'Payment S/N',
            'Amount Due',
            'Payment Due to Client',
            'Balance',
            'DAA Commission',
            'Sales Commission',
        ]
        [worksheet.write(row, header_cell, payment_header[header_cell], header_style) for header_cell in range(0, len(payment_header)) if payment_header[header_cell]]
        for case in self.env['daa.case'].browse(case_ids):
            for payment in case.payment_ids:
                row += 1

                worksheet.write(row, 0, payment.entry_date, text_style)
                worksheet.write(row, 1, payment.invoice_id.invoice_no or '', text_style)
                worksheet.write(row, 2, payment.received_amount or '', number_style)
                worksheet.write(row, 3, payment.received_amount or '', number_style)
                worksheet.write(row, 4, payment.balance_amount or '', number_style)
                worksheet.write(row, 5, payment.received_amount * 6.4 / 100 or '', number_style)
                worksheet.write(row, 6, payment.received_amount * 1.6 / 100 or '', number_style)

        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        attachment = self.env['ir.attachment'].create({
            'name': '%s.xlsx' % (self.name),
            'res_id': self.id,
            'res_model': 'co.wizard',
            'datas': result,
            'type': 'binary',
        })
        download_url = '/web/content/' + str(attachment.id) + '?download=True'
        return {
            "type": "ir.actions.act_url",
            "url": str(download_url)
        }