import json
import logging
import requests

from odoo import http
from odoo.http import request,Response
from odoo.exceptions import Warning
from datetime import datetime
_logger = logging.getLogger(__name__)


class CustomFacebookControllerValidation(http.Controller):

    @http.route('/get_message_from_facebook', type='http',method=['GET'], auth='none')
    def get_message_from_facebook(self, **kwarg):
        if 'hub.verify_token' in kwarg:
            verify_token = kwarg['hub.verify_token']
            active_company = request.env['res.company'].search([('facebook_custom_verify_token','!=',False)],limit=1)
            if active_company.facebook_custom_verify_token == verify_token:
                print("it is authenticated")
            else:
                raise Warning("Security code was not matched")
            challenge = kwarg['hub.challenge']
            if challenge:
                return Response(response=str(challenge), status=200)
        return Response(response=str("something went wrong"), status=500)
    

    
