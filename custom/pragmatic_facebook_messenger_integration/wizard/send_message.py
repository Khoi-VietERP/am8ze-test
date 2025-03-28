from odoo import api,fields,models
import requests
import json
from requests_toolbelt import MultipartEncoder


class SendFacebookMessage(models.TransientModel):
    _name = 'send.facebook.message'
    _description = 'Send Facebook Message'

    facebook_message = fields.Text("Facebook Message")
    multimedia_message = fields.Binary("Multi media message")
    
    def send_facebook_message(self):
        
        if 'active_model' in self._context:
            model = self._context['active_model']
            id = self._context['active_id']
            rec = self.env[model].browse(id)
            if self.facebook_message:
                access_token = rec.company_id.facebook_user_access_token
                headers = {
                    'Content-Type': 'application/json',
                }
                params = (
                    ('access_token', rec.company_id.facebook_page_access_token),
                )
                data = '{ "recipient":{ "id":"'+str(rec.sender_id)+'" }, "message":{ "text":"'+str(self.facebook_message) +'" } }'
                
                url = 'https://graph.facebook.com/v11.0/' + str(rec.company_id.facebook_page_id) +'/messages'
                response = requests.post(url, headers=headers, params=params, data=data)
        
            elif self.multimedia_message:
                headers = {
                    'Content-Type': 'application/json',
                }

                params = {
                    "access_token": rec.company_id.facebook_page_access_token,
                }
                # vals = {
                #     'datas':self.multimedia_message,
                #     'name': 'FB Image'
                # }
                # created_attach = self.env['ir.attachment'].create(vals)
                # print("created_attach ----------",created_attach)

                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                image_url2 = base_url + '/product/image/access/' + 'send.facebook.message/' + str(self.id) + '/multimedia_message'
                print("daim -------------",image_url2)
                # data = '{ "recipient":{ "id":"4227227887392010" }, "message":{ "attachment":{ "type":"image", "payload":{ "url":"http://f678-114-143-52-222.ngrok.io/product/image/access/ir.attachment/81/datas", "is_reusable":true } } } }'
                new_data = '{ "recipient":{ "id":"'+str(rec.sender_id)+'" }, "message":{ "attachment":{ "type":"image", "payload":{ "url":"'+str(image_url2)+'", "is_reusable":true } } } }'
                # print("\n \n data ---------",data)
                print("\n \n new_data ---------",new_data)
                # print(daim)
                r = requests.post("https://graph.facebook.com/v11.0/me/messages", params=params, headers=headers, data=new_data)
                print("r ------------",r,r.status_code)
                print("rrrrrrrrrrr ---",r.text)

                






