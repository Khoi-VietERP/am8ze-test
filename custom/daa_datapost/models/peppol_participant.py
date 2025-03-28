# -*- coding: utf-8 -*-

import csv
import requests
from datetime import datetime
from odoo import api, fields, models, _
from odoo.modules.module import get_module_resource

class PeppolParticipant(models.Model):
    _name = 'peppol.participant'
    # _auto = False

    name = fields.Char('Peppol ID')
    company_name = fields.Char('Company name')
    document_type = fields.Char('Document Types Supported')
    date_registered = fields.Char('Date Registered')

    @api.model
    def cron_update_peppol_participant(self):
        raw_data = self.download_peppol_participants()
        csv_data = raw_data.splitlines()

        participants = self.read_csv(csv_data)
        index = 0
        for participant in participants:
            index += 1

            if participant.get('name', False):
                existing = self.search([
                    ('name', '=', participant.get('name'))
                ])
                if existing and existing.id:
                    continue
                    # existing.write(participant)
                else:
                    self.create(participant)

            if index % 100 == 0:
                self.env.cr.commit()

    @api.model
    def init_peppol_participants(self):
        csv_data_path = get_module_resource('daa_datapost', 'data/', 'peppol.csv')
        with open(csv_data_path, newline='') as csv_data:
            participants = self.read_csv(csv_data)
            index = 0
            for participant in participants:
                index += 1

                if participant.get('name', False):
                    existing = self.search([
                        ('name', '=', participant.get('name'))
                    ])
                    if existing and existing.id:
                        continue
                        # existing.write(participant)
                    else:
                        self.create(participant)

                if index % 100 == 0:
                    self.env.cr.commit()

    @api.model
    def download_peppol_participants(self):
        url = 'https://api.peppoldirectory.sg/private/api/search/export'
        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJnZ3ctZGlyZWN0b3J5IiwianRpIjoiNDNhZDliNWUtMDBiMi00OGQyLWFhYTgtMDA1M2Y1NTY3MzUxIiwiYXVkIjoiZ2d3LWRpcmVjdG9yeS11c2VyIiwic3ViIjoiZGVzbW9uZC5jaG93QGFtOHplLmNvbSIsImV4cCI6MTkzNDUwODA4NSwidHlwIjoiQVBJX0FDQ0VTU19UT0tFTiIsInJvbCI6WyJST0xFX0FQSSIsIlJPTEVfVVNFUiJdfQ.wEKr2t8yLqsm6UgBCwrTg9f1xfmOHeFtOhmqtodgSP5hutq4jTKqCU_LbjPLUqFFHQknzzs8bT53rZNMAKCZAw'
        }

        response = requests.request('GET', url, headers=headers)

        return response.text

    @api.model
    def read_csv(self, csv_data):
        result = []

        reader = csv.reader(csv_data, delimiter=';')
        parsed_data = list(reader)
        index = 0
        for row in parsed_data:
            index += 1
            if index == 1:
                continue # Skip header, first line
            if len(row) == 4:
                date_registered = datetime.strptime(row[3], '%d/%m/%Y')
                line_data = {
                    'name': row[0] or '',
                    'company_name': row[1] or '',
                    'document_type': row[2] or '',
                    'date_registered': date_registered,
                }
                result.append(line_data)

        return result

    # "0195:SGUEN202005798N";
    # "  The Skin Professional Studio Pte Ltd";
    # "SG PEPPOL BIS Billing 3.0 Credit Note [169],SG PEPPOL BIS Billing 3.0 Invoice [168]";
    # "18/03/2021"
