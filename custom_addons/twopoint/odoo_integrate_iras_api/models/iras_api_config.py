# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import base64
import json
import webbrowser
from odoo.exceptions import UserError

class iras_api_config(models.Model):
    _name = 'iras.api.config'
    _description = 'IRAS API Config'

    url = fields.Char(string="URL")
    url_callback = fields.Char(string="URL Callback")
    client_id = fields.Char(string="Client-Id")
    client_secret = fields.Char(string="Client-Secret")
    note = fields.Text('Note')
    callback_history_ids = fields.One2many('iras.api.history', 'iras_api_config_id')

    def get_authorisation_code(self, state=False, scope=False):
        callback_url = self.url_callback
        state = state or 'test'
        url = "%s/iras/sb/Authentication/CorpPassAuth?scope=%s&callback_url=%s&tax_agent=false&state=%s" % (self.url, scope, callback_url, state)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-IBM-Client-Id": self.client_id,
            "X-IBM-Client-Secret": self.client_secret,
        }
        payload = {}
        r = requests.request("GET", url, headers=headers, data=payload)
        result = r.json()
        data = result.get('data', False)
        if data:
            redirect_url = data.get('url', False)
            if redirect_url:
                return {
                    'type': 'ir.actions.act_url',
                    'url': redirect_url,
                    'target': 'new'
                }

        else:
            try:
                message = result.get('info').get('fieldInfoList')[0].get('message')
            except:
                message = 'API: Scope mismatch with client registered scope'
            raise UserError(message)
        return result

    def get_access_token(self, code = False, state = False, scope = False):
        url = self.url +  "/iras/sb/Authentication/CorpPassToken"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-IBM-Client-Id": self.client_id,
            "X-IBM-Client-Secret": self.client_secret,
        }

        payload = {
            "scope" : scope,
            "callback_url" : self.url_callback,
            "code" : code,
            "state" : state,
        }

        r = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        result = r.json()
        data = result.get('data', False)
        if data:
            token = data.get('token', False)
            if token:
                return token
        return False

    def submission_emp_income_action(self, token, iras_submit_id):
        try:
            url = self.url + "/iras/sb/EmpIncomeRecords/Submit"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-IBM-Client-Id": self.client_id,
                "X-IBM-Client-Secret": self.client_secret,
                "access_token": token,
            }

            payload = {
                "inputType": "text",
                "bypass": True,
                "validateOnly": False
             }

            file = base64.b64decode(iras_submit_id.file).decode('utf-8')
            if iras_submit_id.file_type == 'ir8aInput':
                payload.update({
                    "ir8aInput" : file
                })
            if iras_submit_id.file_type == 'ir8sInput':
                payload.update({
                    "ir8sInput" : file
                })
            if iras_submit_id.file_type == 'a8aInput':
                payload.update({
                    "a8aInput" : file
                })
            if iras_submit_id.file_type == 'a8bInput':
                payload.update({
                    "a8bInput" : file
                })

            r = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            result = r.text
        except Exception as e:
            result = "Send error: %s" % e
        return result

    def submission_gst_action(self, token, iras_submit_id):
        if iras_submit_id.gst_file_type in ('F5','F8'):
            dest_url = 'submitF5F8ReturnCorpPass'
        elif iras_submit_id.gst_file_type == 'F7':
            dest_url = 'submitF7ReturnCorpPass'

        try:
            url = self.url + "/iras/sb/gst/" + dest_url
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-IBM-Client-Id": self.client_id,
                "X-IBM-Client-Secret": self.client_secret,
                "access_token": token,
            }

            payload = {
                "filingInfo":
                    {
                        "taxRefNo": "A0064269A",
                        "GstRegNo": "",
                        "formType": "%s" % iras_submit_id.gst_file_type,
                        "dtPeriodStart": "2020-09-01",
                        "dtPeriodEnd": "2020-09-18",
                        "ackNo": "", "pymtRefNo": "",
                        "companyName": "",
                        "dtSubmission": ""
                    },
                "supplies": {
                    "totStdSupply": "198765",
                    "totZeroSupply": "0",
                    "totExemptSupply": "0",
                     "totValueSupply": ""
                    },
                "purchases": {
                    "totTaxPurchase": "30983"
                },
                "taxes": {
                    "outputTaxDue": "13913.55",
                    "inputTaxRefund": "2060.37",
                    "netGSTPaid": ""
                },
                "schemes": {
                    "totValueScheme": "0",
                    "touristRefundChk": "false",
                    "touristRefundAmt": "0",
                    "badDebtChk": "true",
                    "badDebtReliefClaimAmt": "3500",
                    "preRegistrationChk": "false",
                    "preRegistrationClaimAmt": "0"
                },
                "revenue": {
                    "revenue": ""
                },
                "RCElectronicMktplaceOpr": {
                    "RCChk": "false",
                    "totImpServAmt": "0",
                    "OVRChk": "false",
                    "totDigitalServAmt": "0"
                },
                "RevChargeLVG": {
                    "RCLVGChk": "false",
                    "totImpServLVGAmt": "99999999999999"
                },
                "ElectronicMktplaceOprRedlvr": {
                    "OVRRSChk": "false",
                    "totRemServAmt": "99999999999999",
                    "RedlvrMktOprLVGChk": "false",
                    "totRedlvrMktOprLVGAmt": "99999999999999"
                },
                "SupplierOfImpLVG": {
                    "OwnImpLVGChk": "false",
                    "totOwnImpLVGAmt": "99999999999999"
                },
                "igdScheme": {
                    "defNetGst": "",
                    "defImpPayableAmt": "5281.98",
                    "defTotalTaxAmt": "",
                    "defTotalGoodsImp": "75460"
                },
                "declaration": {
                    "declarantID": "",
                    "declarantName": "",
                    "declarantDesgtn": "FM",
                    "contactPerson": "BOOTSTRAP_F8_IGDS_API",
                    "contactNumber": "81234567",
                    "contactEmail": "F8_IGDS@BOOTSTRAP.COM.SG",
                    "declareTrueCompleteChk": "true",
                    "declareIncRtnFalseInfoChk": "true"
                },
                "reasons": {
                    "grp1BadDebtRecoveryChk": "true",
                    "grp1PriorToRegChk": "false",
                    "grp1OtherReasonChk": "false",
                    "grp1OtherReasons": "",
                    "grp2TouristRefundChk": "false",
                    "grp2AppvBadDebtReliefChk": "false",
                    "grp2CreditNotesChk": "false",
                    "grp2OtherReasonsChk": "false",
                    "grp2OtherReasons": "",
                    "grp3CreditNotesChk": "false",
                    "grp3OtherReasonsChk": "false",
                    "grp3OtherReasons": ""
                }
            }

            r = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            result = r.text
        except Exception as e:
            result = "Send error: %s" % e
        return result


class iras_api_history(models.Model):
    _name = 'iras.api.history'
    _description = 'IRAS API History'

    name = fields.Text(string="Description")
    iras_api_config_id = fields.Many2one('iras.api.config')
