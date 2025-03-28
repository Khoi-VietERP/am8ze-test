# -*- coding: utf-8 -*-
import logging
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
import zipfile
from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.http import content_disposition
import ast
import base64
from odoo.addons.web.controllers import main as web
from odoo.addons.web.controllers.main import ExcelExport, ExportXlsxWriter
import json
import io
from odoo.tools.misc import str2bool, xlsxwriter, file_open
import datetime

_logger = logging.getLogger(__name__)


class Binary(http.Controller):
    @http.route('/invoice/download_attachment_invoices', type='http', auth="public")
    def download_attachment_invoices(self, tab_id, **kw):
        new_tab = ast.literal_eval(tab_id)
        attachment_ids = request.env['ir.attachment'].search([('id', 'in', new_tab)])
        if len(attachment_ids) > 1:
            file_dict = {}
            for attachment_id in attachment_ids:
                file_store = attachment_id.store_fname
                if file_store:
                    file_name = "%s.pdf" % attachment_id.name.replace('/', '-')
                    file_path = attachment_id._full_path(file_store)
                    file_dict["%s:%s" % (file_store, file_name)] = dict(path=file_path, name=file_name)
            zip_filename = datetime.now().strftime('%Y-%m-%d_%H:%M')
            zip_filename = "Invoice_%s.zip" % zip_filename
            bitIO = BytesIO()
            zip_file = zipfile.ZipFile(bitIO, "w", zipfile.ZIP_DEFLATED)
            for file_info in file_dict.values():
                zip_file.write(file_info["path"], file_info["name"])
            zip_file.close()
            return request.make_response(bitIO.getvalue(),
                                         headers=[('Content-Type', 'application/x-zip-compressed'),
                                                  ('Content-Disposition', content_disposition(zip_filename))])
        else:
            if attachment_ids:
                attachment_id = attachment_ids[0]
                file_store = attachment_id.store_fname
                if file_store:
                    file_name = "%s.pdf" % attachment_id.name

                filecontent = BytesIO(base64.standard_b64decode(attachment_id.datas))

                return request.make_response(filecontent,
                                             [('Content-Type', 'application/vnd.ms-excel'),
                                              ('Content-Disposition', content_disposition(file_name))])


class Home(web.Home):
    def _login_redirect(self, uid, redirect=None):
        if request.params.get('login_success'):
            try:
                request.env['account.move'].set_invoice_date(False, uid)
            except:
                pass

        return super()._login_redirect(uid, redirect)

class ExportXlsxWriterNew:

    def __init__(self, field_names, row_count=0):
        self.field_names = field_names
        self.output = io.BytesIO()
        self.workbook = xlsxwriter.Workbook(self.output, {'in_memory': True})
        self.base_style = self.workbook.add_format({'text_wrap': True})
        self.header_style = self.workbook.add_format({'bold': True})
        self.bold_style_right = self.workbook.add_format({'bold': True})
        self.header_bold_style = self.workbook.add_format({'text_wrap': True, 'bold': True, 'bg_color': '#e9ecef'})
        self.number_total_style = self.workbook.add_format({'bold': True,'align': 'right','border' : True})
        self.number_total_style.set_num_format('#,##0.00')
        self.date_style = self.workbook.add_format({'text_wrap': True, 'num_format': 'yyyy-mm-dd'})
        self.datetime_style = self.workbook.add_format({'text_wrap': True, 'num_format': 'yyyy-mm-dd hh:mm:ss'})
        self.worksheet = self.workbook.add_worksheet()
        self.value = False

        if row_count > self.worksheet.xls_rowmax:
            raise UserError(_('There are too many rows (%s rows, limit: %s) to export as Excel 2007-2013 (.xlsx) format. Consider splitting the export.') % (row_count, self.worksheet.xls_rowmax))

    def __enter__(self):
        self.write_header()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def write_header(self):
        # Write main header
        for i, fieldname in enumerate(self.field_names):
            self.write(0, i, fieldname, self.header_style)
        self.worksheet.set_column(0, i, 30) # around 220 pixels

    def close(self):
        self.workbook.close()
        with self.output:
            self.value = self.output.getvalue()

    def write(self, row, column, cell_value, style=None):
        self.worksheet.write(row, column, cell_value, style)

    def write_cell(self, row, column, cell_value):
        cell_style = self.base_style

        if isinstance(cell_value, bytes):
            try:
                # because xlsx uses raw export, we can get a bytes object
                # here. xlsxwriter does not support bytes values in Python 3 ->
                # assume this is base64 and decode to a string, if this
                # fails note that you can't export
                cell_value = pycompat.to_text(cell_value)
            except UnicodeDecodeError:
                raise UserError(_("Binary fields can not be exported to Excel unless their content is base64-encoded. That does not seem to be the case for %s.") % self.field_names[column])

        if isinstance(cell_value, str):
            if len(cell_value) > self.worksheet.xls_strmax:
                cell_value = _("The content of this cell is too long for an XLSX file (more than %s characters). Please use the CSV format for this export.") % self.worksheet.xls_strmax
            else:
                cell_value = cell_value.replace("\r", " ")
        elif isinstance(cell_value, datetime.datetime):
            cell_style = self.datetime_style
        elif isinstance(cell_value, datetime.date):
            cell_style = self.date_style
        self.write(row, column, cell_value, cell_style)


class ExcelExportView(ExcelExport):

    def from_data(self, fields, rows):
        check_account_payment = False
        if request.params.get('data', False):
            data = json.loads(request.params.get('data', False))
            if data.get('model', False) == 'account.payment':
                check_account_payment = True

        if check_account_payment:

            with ExportXlsxWriterNew(fields, len(rows)) as xlsx_writer:
                total_list = {}
                end_row = 0
                for row_index, row in enumerate(rows):
                    for cell_index, cell_value in enumerate(row):
                        if isinstance(cell_value, (list, tuple)):
                            cell_value = pycompat.to_text(cell_value)
                        if isinstance(cell_value, (float)):
                            total_list.update({
                                cell_index : total_list.get(cell_index, 0) + cell_value
                            })
                        xlsx_writer.write_cell(row_index + 1, cell_index, cell_value)
                        end_row = row_index + 1

                if total_list:
                    first = True
                    for index, value in total_list.items():
                        if first and index > 0:
                            xlsx_writer.write(end_row + 1, index - 1, 'Total :', xlsx_writer.bold_style_right)
                            first = False
                        xlsx_writer.write(end_row + 1, index, value, xlsx_writer.number_total_style)
        else:
            with ExportXlsxWriter(fields, len(rows)) as xlsx_writer:
                for row_index, row in enumerate(rows):
                    for cell_index, cell_value in enumerate(row):
                        if isinstance(cell_value, (list, tuple)):
                            cell_value = pycompat.to_text(cell_value)
                        xlsx_writer.write_cell(row_index + 1, cell_index, cell_value)

        return xlsx_writer.value
