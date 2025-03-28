
from odoo import models, fields, api
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

import base64
from io import BytesIO

class sale_history_report(models.TransientModel):
    _name = 'sale.history.report'

    start_date = fields.Date('Start Date', required=1)
    end_date = fields.Date('End Date')
    partner_id = fields.Many2one('res.partner', String="Customer")
    product_id = fields.Many2one('product.product', 'Item')
    is_best_selling_report = fields.Boolean(default=False)


    def get_data_report(self):

        conditions = [('order_id.state', 'in', ['sale','done'])]
        if self.start_date:
            conditions.append(('order_id.date_order', '>=', self.start_date))
        if self.end_date:
            conditions.append(('order_id.date_order', '<=', self.end_date))
        if self.partner_id:
            conditions.append(('order_id.partner_id', '=', self.partner_id.id))
        if self.product_id:
            conditions.append(('product_id', '=', self.product_id.id))

        datas = self.env['sale.order.line'].read_group(conditions, ['product_id', 'price_total', 'product_uom_qty'], ['product_id'])

        data_report = []
        for line in datas:
            if line['product_id']:
                product_id = self.env['product.product'].browse(line['product_id'][0])
                data_report.append({
                    'product_name': product_id.name,
                    'product_total': line['price_total'],
                    'product_unit': line['product_uom_qty'],
                    'cost_of_sales': product_id.standard_price * line['product_uom_qty'],
                })

        if self.is_best_selling_report:
            data_report = sorted(data_report, key=lambda data: data['product_unit'], reverse=True)

        return data_report

    def generate_xlsx_report(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Sale History Report')

        header_style = workbook.add_format({
            'bold': True,
            'italic': True,
            'font_size': '12',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        })

        worksheet.set_column('A:A', 50)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:I', 15)

        summary_header = [
            'Product',
            'Sales Amount',
            'Unit',
            'Cost of Sales',
        ]
        row = 0
        [worksheet.write(row, header_cell, summary_header[header_cell], header_style) for header_cell in
         range(0, len(summary_header)) if summary_header[header_cell]]

        data_report = self.get_data_report()

        for line in data_report:
            row += 1
            worksheet.write(row, 0, line['product_name'])
            worksheet.write(row, 1, line['product_total'])
            worksheet.write(row, 2, line['product_unit'])
            worksheet.write(row, 3, line['cost_of_sales'])


        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        attachment = self.env['ir.attachment'].create({
            'name': 'Sale History Report.xlsx',
            'res_id': self.id,
            'res_model': 'sale.history.report',
            'datas': result,
            'type': 'binary',
        })
        download_url = '/web/content/' + str(attachment.id) + '?download=True'
        return {
            "type": "ir.actions.act_url",
            "url": str(download_url)
        }
