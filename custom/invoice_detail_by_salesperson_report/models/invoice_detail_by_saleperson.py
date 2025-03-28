# -*- coding: utf-8 -*-

from odoo import models, fields, api
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

import base64
from io import BytesIO


class invoice_detail_by_saleperson(models.TransientModel):
    _name = 'invoice.detail.by.saleperson'

    start_date = fields.Date('Start Date', required=1)
    end_date = fields.Date('End Date')
    user_id = fields.Many2one('res.users', string='Saleperson')

    def get_datas(self):
        domain = [('type', '=', 'out_invoice')]
        if self.start_date:
            domain.append(('invoice_date', '>=', self.start_date))
        if self.end_date:
            domain.append(('invoice_date', '<=', self.end_date))

        user_ids = self.env['account.move'].search(domain).mapped('invoice_user_id')
        if self.user_id:
            user_ids = self.user_id

        datas = {}
        for user_id in user_ids:
            new_domain = domain + [('user_id', '=', user_id.id)]

            invoice_ids = self.env['account.move'].search(new_domain)
            lines = []
            for invoice_id in invoice_ids:
                delivery_date = ''
                warehouse = ''
                if invoice_id.invoice_origin:
                    delivery_id = self.env['stock.picking'].search(
                        [('origin', '=', invoice_id.invoice_origin), ('picking_type_id.code', '=', 'outgoing')], limit=1)
                    if delivery_id:
                        delivery_date = delivery_id.date_done and delivery_id.date_done.strftime('%d/%m/%Y') or ''
                        warehouse = delivery_id.picking_type_id.warehouse_id.name
                for line in invoice_id.invoice_line_ids:
                    if not line.display_type:
                        lines.append({
                            'customer_name' : invoice_id.partner_id.name,
                            'invoice_number' : invoice_id.name or '',
                            'invoice_date' : invoice_id.invoice_date and invoice_id.invoice_date.strftime('%d/%m/%Y') or '',
                            'po_number' : '',
                            'delivery_date' : delivery_date,
                            'product_name' : line.name,
                            'gl_account' : '',
                            'qty' : line.quantity,
                            'price' : line.price_unit,
                            'gst_amt' : line.price_total - line.price_subtotal,
                            'cost' : line.product_id.standard_price * line.quantity,
                            'amount_paid' : invoice_id.amount_residual - invoice_id.amount_total,
                            'warehouse' : warehouse,
                        })
            if lines:
                datas.update({
                    user_id : lines
                })

        return datas

    def generate_xlsx_report(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Sale Detail By Saleperson Report')

        title1_style = workbook.add_format({
            'bold': True,
            'font_size': '18',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        title2_style = workbook.add_format({
            'bold': True,
            'font_size': '15',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        header_style = workbook.add_format({
            'bold': True,
            'italic': True,
            'font_size': '12',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        text_style_left = workbook.add_format({
            'bold': False,
            'italic': False,
            'font_size': '12',
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
        })

        text_style_left_bold = workbook.add_format({
            'bold': True,
            'italic': False,
            'font_size': '12',
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
        })

        text_style_center = workbook.add_format({
            'bold': False,
            'italic': False,
            'font_size': '12',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        number_style = workbook.add_format({
            'bold': False,
            'italic': False,
            'font_size': '12',
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
        })
        number_style.set_num_format('#,##0.00')

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:E', 20)
        worksheet.set_column('F:F', 60)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:L', 15)
        worksheet.set_column('M:M', 20)

        worksheet.merge_range(0, 0, 0, 12, 'Sale Detail By Saleperson Report',title1_style)
        worksheet.merge_range(1, 0, 1, 12, 'For the Period From %s To %s' % (self.start_date,self.end_date),title2_style)
        worksheet.merge_range(2, 0, 2, 12, '', title1_style)

        summary_header = [
            'Customer Code / Name',
            'Invoice number',
            'Invoice date',
            'PO number',
            'Delivery date',
            'Item No. and Description',
            'GL account posted to',
            'Qty / Units',
            'Price b/f GST',
            'GST Amt',
            'Cost',
            'Amount Paid',
            'Warehouse',
        ]
        row = 3
        [worksheet.write(row, header_cell, summary_header[header_cell], header_style) for header_cell in
         range(0, len(summary_header)) if summary_header[header_cell]]

        datas = self.get_datas()

        for key,values in datas.items():
            row += 1
            worksheet.merge_range(row, 0, row, 12, key.name,text_style_left_bold)
            for line in values:
                row += 1
                worksheet.write(row, 0, line['customer_name'], text_style_left)
                worksheet.write(row, 1, line['invoice_number'], text_style_left)
                worksheet.write(row, 2, line['invoice_date'], text_style_left)
                worksheet.write(row, 3, line['po_number'], text_style_left)
                worksheet.write(row, 4, line['delivery_date'], text_style_left)
                worksheet.write(row, 5, line['product_name'], text_style_left)
                worksheet.write(row, 6, line['gl_account'], text_style_left)
                worksheet.write(row, 7, line['qty'], number_style)
                worksheet.write(row, 8, line['price'], number_style)
                worksheet.write(row, 9, line['gst_amt'], number_style)
                worksheet.write(row, 10, line['cost'], number_style)
                worksheet.write(row, 11, line['amount_paid'], number_style)
                worksheet.write(row, 12, line['warehouse'], text_style_left)

        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        attachment = self.env['ir.attachment'].create({
            'name': 'Sale Detail By Saleperson.xlsx',
            'res_id': self.id,
            'res_model': 'invoice.detail.by.saleperson',
            'datas': result,
            'type': 'binary',
        })
        download_url = '/web/content/' + str(attachment.id) + '?download=True'
        return {
            "type": "ir.actions.act_url",
            "url": str(download_url)
        }