# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import binascii
import tempfile
import base64
import xlrd
import csv
from io import StringIO

identification_dict = {
    'NRIC' : '1',
    'FIN' : '2',
    'Immigration File Ref No.' : '3',
    'Work Permit No' : '4',
    'Malaysian I/C (for non-resident director and seaman only)' : '5',
    'Passport No. (for non-resident director and seaman only)' : '6',
}

address_type_dict = {
    'Local residential address' : 'L',
    'Foreign address' : 'F',
    'Local C/O address' : 'C',
    'Not Available' : 'N',
}

cessation_provisions_dict = {
    'Cessation Provisions applicable': 'Y',
    'Cessation Provisions not applicable': 'N',
}

class import_employee(models.TransientModel):
    _name = 'import.employee'

    name = fields.Char(string="Name")
    file = fields.Binary('File', required=1)

    def get_date(self, wb, date):
        date_convert = False
        if date:
            try:
                year, month, day, hour, minutes, seconds = xlrd.xldate_as_tuple(date,wb.datemode)
                date_convert = '{:04d}{:02d}{:02d}'.format(year, month, day)
                date_convert = datetime.strptime(date_convert, '%Y%m%d')
            except:
                try:
                    date_convert = datetime.strptime(date, '%d/%m/%Y')
                except:
                    pass
        return date_convert

    def import_product_data(self):
        address_home_obj = self.env['res.partner'].with_context(default_type='private')
        res_country_obj = self.env['res.country']
        state_obj = self.env['res.country.state']
        race_obj = self.env['employee.race']
        job_obj = self.env['hr.job']
        hr_department_obj = self.env['hr.department']
        hr_employee_obj = self.env['hr.employee']

        try:
            csv_data = base64.b64decode(self.file)
            data_file = StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            csv_reader = csv.reader(data_file, delimiter=',')
            file_reader.extend(csv_reader)

        except:
            raise Warning(_("Invalid file!"))

        for i in range(len(file_reader)):
            field = list(map(str, file_reader[i]))
            employee_data = {}
            if i == 0:
                continue
            else:
                birthday = False
                if field[2]:
                    birthday = datetime.strptime(field[2],'%d/%m/%Y')
                address_home_id = address_home_obj
                if field[7] or field[8] or field[9] or field[10] or field[11]:
                    emp_country_id = res_country_obj.search([('name', '=', field[11])], limit=1)
                    state_id = state_obj.search([('name', '=', field[9])], limit=1)
                    address_home_id = address_home_obj.create({
                        'name': field[0] + " address",
                        'zip': str(field[10]).replace('.0', '') if field[10] else '',
                        'street': field[7],
                        'country_id': emp_country_id.id,
                        'city': field[8],
                        'state_id': state_id.id,
                    })
                country_id = res_country_obj.search([('name', '=', field[12])], limit=1)
                race_id = race_obj.search([('name', '=', field[22])], limit=1)
                job_id = job_obj.search([('name', '=', field[25])], limit=1)
                department_id = hr_department_obj.search([('name', '=', field[26])], limit=1)

                employee_data.update({
                    'name' : field[0],
                    'gender' : field[1].lower() if field[1] else False,
                    'birthday' : birthday,
                    'work_email' : field[3],
                    'identification_id' : field[5],
                    'mobile_phone' : field[6],
                    'address_home_id' : address_home_id.id,
                    'country_id' : country_id.id,
                    'marital' : field[13].lower() if field[13] else False,
                    'phone' : field[14],
                    'work_phone' : field[15],
                    'join_date': datetime.strptime(field[21],'%d/%m/%Y') if field[21] else '',
                    'race_id': race_id.id,
                    'job_id': job_id.id,
                    'department_id': department_id.id,
                    'singaporean': True if field[27] and field[27].lower() == 'true' else False,
                    'pr_date': datetime.strptime(field[28],'%d/%m/%Y') if field[28] else '',
                })
                hr_employee_exist = self.env['hr.employee']
                if field[5]:
                    hr_employee_exist = hr_employee_exist.search([('identification_id', '=', field[5])], limit=1)
                    if hr_employee_exist:
                        hr_employee_exist.write(employee_data)
                if not hr_employee_exist:
                    hr_employee_obj.create(employee_data)