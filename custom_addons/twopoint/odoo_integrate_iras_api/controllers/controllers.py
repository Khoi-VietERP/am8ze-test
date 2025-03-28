# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import base64

class OdooIntegrateIrasApi(http.Controller):

    @http.route(['/iras_callback'], type='http', auth='none', csrf=False, method=['GET', 'POST'])
    def iras_callback(self, **kwargs):
        try:
            code = kwargs.get('code', '')
            state = kwargs.get('state', '')
            scope = kwargs.get('scope', '')
            iras_api_config_id = request.env.ref('odoo_integrate_iras_api.iras_api_config_data')
            iras_api_config_id.write({
                'callback_history_ids': [(0, 0, {
                    'name': str(kwargs),
                })]
            })

            iras_submit_id = request.env['iras.api.submit'].search([('name', '=', state)], limit=1)
            token = iras_api_config_id.get_access_token(code, state, scope)
            if token:
                if iras_submit_id.api_type == 'submission_emp_income':
                    result = iras_api_config_id.submission_emp_income_action(token, iras_submit_id)
                elif iras_submit_id.api_type == 'submission_gst':
                    result = iras_api_config_id.submission_gst_action(token, iras_submit_id)
                iras_submit_id.write({
                    'note' : result,
                    'state' : 'submit'
                })
            else:
                iras_submit_id.write({
                    'note': 'Can not get Token',
                    'state': 'error'
                })
        except:
            iras_api_config_id = request.env.ref('odoo_integrate_iras_api.iras_api_config_data')
            iras_api_config_id.note = 'error'
