# -*- coding: utf-8 -*-
import uuid
import json
import requests
import base64
from datetime import datetime, timedelta
from odoo import models, fields, api


class DatapostApi(models.Model):
    _name = 'datapost.api'

    name = fields.Char('Name')
    root_uri = fields.Char('Root URI', required=True, default='https://peppol.datapost.com.sg')
    base_uri = fields.Char('Base URI', required=True, default='https://peppol.datapost.com.sg/services/rest/peppol')
    api_version = fields.Selection([
        ('v10', 'v1.0'),
    ], string='API Version', required=True, default='v10')
    api_key = fields.Char('API Key', required=True)
    api_secret = fields.Char('API Secret', required=True)
    token_ids = fields.One2many('datapost.token', 'api_id', string='Tokens')

    peppol_db_name = fields.Char(string="Peppol DB Name")
    peppol_url = fields.Char(string="Peppol DB URL")
    peppol_login = fields.Char(string="Peppol DB Login")
    peppol_password = fields.Char(string="Peppol DB Password")

    def get_datapost_token_uri(self):
        self.ensure_one()

        uri = '%s/app/services/rest/auth/token' % self.root_uri
        return uri

    def get_datapost_token_refresh_uri(self):
        self.ensure_one()

        uri = '%s/app/services/rest/auth/refreshToken' % self.root_uri
        return uri

    def get_datapost_uri(self):
        self.ensure_one()
        base_uri = self.base_uri
        version = self.api_version

        uri = '%s/business/%s' % (base_uri, version)
        return uri

    def get_document_url(self, document, force_new=False):
        url = False
        uri = self.get_datapost_uri()

        ref = self.get_document_ref(document, force_new=force_new)
        if document.document_type == 'invoice':
            url = f'{uri}/invoices/peppol-invoice-2/{ref}'
        elif document.document_type == 'creditnote':
            url = f'{uri}/credit-notes/peppol-credit-note-2/{ref}'
        elif document.document_type == 'order':
            url = f'{uri}/orders/peppol-order-2/{ref}'
        elif document.document_type == 'invoice-response':
            url = f'{uri}/invoice-responses/peppol-invoice-response-2/{ref}'
        elif document.document_type == 'order-response':
            url = f'{uri}/order-responses/peppol-order-response-2/{ref}'

        return url

    @api.model
    def get_received_documents_url(self, documentType):
        uri = self.get_datapost_uri()

        url = f'{uri}/{documentType}.json?type=2'
        return url

    @api.model
    def get_received_document_url(self, documentType, documentNo):
        uri = self.get_datapost_uri()

        url = f'{uri}/{documentType}/{documentNo}.xml'
        return url

    @api.model
    def get_document_ref(self, document, force_new=False):
        ref = document.client_ref_uuid
        if force_new:
            ref = False
        if not ref:
            ref = str(uuid.uuid4())
            document.client_ref_uuid = ref
        return ref

    def _convert_expiration_to_datetime(self, expiration):
        date_format = '%m/%d/%Y %H:%M'
        result = datetime.strptime(expiration, date_format) - timedelta(hours=8)
        return result

    def _get_datapost_token(self):
        self.ensure_one()
        result = {}

        url = self.get_datapost_token_uri()
        headers = {
            'Content-Type': 'application/json'
        }
        payload = json.dumps({
            'clientId': self.api_key,
            'secret': self.api_secret
        })

        response = requests.request('POST', url, headers=headers, data=payload)
        if response.status_code == 200:
            data = json.loads(response.text)
            result = {
                'api_id': self.id,
                'access_token': data.get('access_token', False),
                'access_token_expiration': self._convert_expiration_to_datetime(data.get('access_token_expiration')),
                'refresh_token': data.get('refresh_token', False),
                'refresh_token_expiration': self._convert_expiration_to_datetime(data.get('refresh_token_expiration')),
            }

        return result

    def _get_datapost_token_refresh(self, refresh_token):
        self.ensure_one()
        result = {}

        url = self.get_datapost_token_refresh_uri()
        headers = {
            'Content-Type': 'application/json'
        }
        payload = json.dumps({
            'refresh_token': refresh_token,
        })

        response = requests.request('POST', url, headers=headers, data=payload)
        if response.status_code == 200:
            data = json.loads(response.text)
            result = {
                'access_token': data.get('access_token', False),
                'access_token_expiration': self._convert_expiration_to_datetime(data.get('access_token_expiration')),
                'refresh_token': data.get('refresh_token', False),
                'refresh_token_expiration': self._convert_expiration_to_datetime(data.get('refresh_token_expiration')),
            }

        return result

    def get_datapost_token(self):
        self.ensure_one()
        token = False

        for _token in self.token_ids:
            if _token.is_valid:
                token = _token
                break
            elif _token.can_refresh:
                token_data = self._get_datapost_token_refresh(_token.refresh_token)
                if token_data:
                    _token.write(token_data)
                    token = _token
                    break

        if not token:
            token_data = self._get_datapost_token()
            token = self.env['datapost.token'].create(token_data)

        return token

    def get_document_files(self, documents):
        files = []
        for document in documents:
            if not document.xml_file:
                document.action_generate_document()
            files.append(
                ('document', ('%s.xml' % (document.id or 'Invoice'), base64.b64decode(document.xml_file).decode('utf8'), 'text/xml'))
            )
        return files

    def get_datapost_authorization(self):
        self.ensure_one()

        headers = {}
        token = self.get_datapost_token()
        if token:
            headers = {"Authorization": "Bearer %s" % token.access_token}
        return headers

    def send_document(self, document):
        self.ensure_one()

        url = self.get_document_url(document, force_new=True)
        headers = self.get_datapost_authorization()
        files = self.get_document_files([document])

        result = requests.request('PUT', url, headers=headers, files=files)
        return {
            'status': result.status_code,
            'data': result.text,
        }

    @api.model
    def get_received_documents(self, documentType):
        url = self.get_received_documents_url(documentType)
        headers = self.get_datapost_authorization()

        result = requests.request('GET', url, headers=headers)
        return {
            'status': result.status_code,
            'data': result.text,
        }

    @api.model
    def get_received_document(self, documentType, documentNo):
        url = self.get_received_document_url(documentType, documentNo)
        headers = self.get_datapost_authorization()

        result = requests.request('GET', url, headers=headers)
        return {
            'status': result.status_code,
            'data': result.text,
        }