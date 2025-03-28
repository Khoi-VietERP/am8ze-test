import json
import logging
import requests
import base64

from odoo import http
from odoo.http import request,Response
from odoo.exceptions import Warning
from datetime import datetime



_logger = logging.getLogger(__name__)


class CustomFacebookController(http.Controller):

    
    @http.route('/get_message_from_facebook', type='json',method=['POST'], auth='none')
    def get_message_from_facebook_response(self, **kwarg):
        data = json.loads(request.httprequest.data)
        if 'entry' in data:
            entries = data['entry']
            for data_entry in entries:
                message_id = data_entry['id']
                # message_rec = request.env['facebook.message'].search([('message_id','=',message_id)],limit=1)
                for entry in data_entry['messaging']:
                    sender_id = entry['sender']['id']
                    reciepient_id = entry['recipient']['id']
                    message_rec = request.env['facebook.message'].search([('sender_id','=',sender_id),('reciever_id','=',reciepient_id)],limit=1)
                    if not message_rec:
                        message_rec = request.env['facebook.message'].search([('sender_id','=',reciepient_id),('reciever_id','=',sender_id)],limit=1)


                    if not message_rec:
                        data_vals={
                            'message_id':message_id,
                            'sender_id':sender_id,
                            'reciever_id':reciepient_id,
                        }
                        company = request.env['res.company'].search([('facebook_page_id','!=',False)],limit=1)
                        if company:
                            data_vals['company_id'] = company.id
                        message_rec = request.env['facebook.message'].create(data_vals)

                    if message_rec:
                        line_vals = {
                            'message_id':message_rec.id,
                        }
                        if message_rec.company_id:
                            timestamp = str(entry['timestamp'])
                            timestamp = timestamp[:-3]
                            ts = int(timestamp)
                            converted_time = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                            if message_rec.company_id.facebook_page_id == entry['sender']['id']:
                                line_vals['message_type'] = 'outgoing'
                                line_vals['date_sent'] = converted_time
                            else:
                                line_vals['message_type'] = 'incoming'
                                line_vals['date_recieved'] = converted_time
                        
                        if 'message' in entry:
                            if 'text' in entry['message']:
                                line_vals['text_message'] = entry['message']['text']
                                line_vals['file_message_type'] = 'text'
                            elif 'attachments' in entry['message']:
                                attachments = entry['message']['attachments']
                                for attachment in attachments:
                                    if attachment['type'] == 'image':
                                        url = attachment['payload']['url']
                                        line_vals['file_message_link'] = url
                                        data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
                                        line_vals['file_message']= data

                            if 'mid' in entry:
                                line_vals['message_seq'] = entry['message']['mid']
                        if 'text_message' in line_vals or 'file_message' in line_vals:
                            request.env['facebook.message.line'].create(line_vals)

        
        return Response(response=str("ok"), status=200)
