# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import base64
from mailmerge import MailMerge
from lxml import etree
import binascii
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from datetime import datetime,date
import logging
import pytz

_logger = logging.getLogger(__name__)
try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def create_attachment_report(self, filename, reportname, model, docid, data={}):

        report = self.env.ref(reportname)
        datas = self.env[model].search([('id', '=', docid)])

        docx = report.with_context(data=data).render_doc_doc(datas, data=data)[0]

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(docx),
            'store_fname': filename,
            'res_model': model,
            'res_id': docid,
            'mimetype': 'application/x-pdf'
        })


    def export_doc_by_template(self, file_template_data=None, suffix='docx', file_name_export='export1', datas={}):
        simple_merge = {}
        populating_tables = {}
        file_template = self._convert_binary_to_doc(file_template_data=file_template_data,suffix=suffix)
        document = MailMerge(file_template.name)
        fields = document.get_merge_fields()
        context_data = self._context.get('data')

        datetime_utc = pytz.timezone('UTC')


        for field in fields:
            childs = field.split('.')
            check = False
            if childs[0] == 'datalines':
                check = True
            if context_data.get(field, False) or check:
                if context_data.get(field, False):
                    simple_merge[field] = context_data.get(field, False)
                else:
                    tmp_val = []
                    value_field = {}
                    key = childs[0]
                    field_data = context_data.get('%s.%s'%(childs[0],childs[1]), False)
                    for data in field_data:
                        tmp_val.append(data.get(childs[2]))
                    value_field[field] = tmp_val
                    if key in populating_tables:
                        populating_tables[key].append(value_field)
                    else:
                        tmp_value = []
                        tmp_value.append(value_field)
                        populating_tables[key] = tmp_value
            else:
                childs = field.split('.')
                if len(childs) == 1:
                    value = getattr(datas, childs[0], '')
                    if isinstance(value, datetime):
                        value = self._convert_datetime_usertz_to_utctz(value)
                    elif isinstance(value, date):
                        value = value.strftime(self.env['res.lang'].search([('code', '=', self.env.user.lang)], limit=1).date_format)
                    elif isinstance(value, bool):
                        if value == False:
                            value = ''
                        else:
                            value = str(value)
                    else:
                        value = str(value)
                    simple_merge[field] = value
                else:
                    if childs[0] == 'line':
                        childs.remove(childs[0])
                        key = childs[0]
                        data_array = getattr(datas, key)
                        childs.remove(key)
                        tmp_val = []
                        value_field = {}
                        numerical_order = 0
                        for data in data_array:
                            for child in childs:
                                if child == 'numerical_order':
                                    data = numerical_order + 1
                                    numerical_order = data
                                elif child == "float_time":
                                    hour, minute = divmod(data * 60, 60)
                                    x_tmp = "%02d:%02d" % (hour, minute)
                                    data = x_tmp
                                else:
                                    data = getattr(data, child)

                            if isinstance(data, (float, int)) == False and data == False:
                                data = ''
                            elif type(data) == bool:
                                data = ''
                            elif isinstance(data, datetime):
                                data = self._convert_datetime_usertz_to_utctz(data)
                            elif isinstance(data, date):
                                data = data.strftime(
                                    self.env['res.lang'].search([('code', '=', self.env.user.lang)], limit=1).date_format)
                            else:
                                data = str(data)
                            tmp_val.append(data)

                        value_field[field] = tmp_val
                        if key in populating_tables:
                            populating_tables[key].append(value_field)
                        else:
                            tmp_value = []
                            tmp_value.append(value_field)
                            populating_tables[key] = tmp_value
                    else:
                        if len(childs) <= 0:
                            continue
                        tmp_logic = childs[len(childs)-1]
                        if tmp_logic == 'sum':
                            data_array = getattr(datas, childs[0])
                            sum = 0
                            for data in data_array:
                                value = getattr(data, childs[1])
                                sum += value
                            simple_merge[field] = str(sum)
                        elif tmp_logic == 'count':
                            data_array = getattr(datas, childs[0])
                            count = len(data_array)
                            simple_merge[field] = str(count)
                        elif tmp_logic == 'sum_number2word':
                            data_array = getattr(datas, childs[0])
                            sum = 0
                            for data in data_array:
                                value = getattr(data, childs[1])
                                sum += value
                            num_to_char = self.num2word(sum)
                            simple_merge[field] = num_to_char
                        else:
                            data = datas
                            for child in childs:
                                data = getattr(data,child)
                            simple_merge[field] = str(data)

        document.merge(**simple_merge)

        for key in populating_tables:
            value = populating_tables[key]
            list = []
            anchor = ''
            number = 0
            if number == 0:
                for k in value[0]:
                    val = value[0][k]
                    number = len(val)
                    break
            for i in range(number):
                dict = {}
                for val in value:
                    for k in val:
                        v = val[k]
                        dict[k] = v[i]
                        if anchor == '':
                            anchor = k
                        break
                list.append(dict)
            document.merge_rows(anchor, list)

        for field in document.get_merge_fields():
            document.merge(**{field: ''})

        mem_zip = BytesIO()
        with ZipFile(mem_zip, 'w', ZIP_DEFLATED) as output:
            for zi in document.zip.filelist:
                if zi in document.parts:
                    xml = etree.tostring(document.parts[zi].getroot())
                    output.writestr(zi.filename, xml)
                elif zi == document._settings_info:
                    xml = etree.tostring(document.settings.getroot())
                    output.writestr(zi.filename, xml)
                else:
                    output.writestr(zi.filename, document.zip.read(zi))

        return mem_zip.getvalue()