from odoo import api,fields,models
import requests
import json
from odoo.exceptions import Warning


class FacebookMessage(models.Model):
    _name = 'facebook.message'
    _description = "Facebook Message"

    sender_id = fields.Char("Sender ID")
    sender_name = fields.Char("Sender name")
    message_id = fields.Char("Message ID")
    message_lines = fields.One2many("facebook.message.line",'message_id',string="message lines")
    reciever_id = fields.Char("Reciever ID")
    company_id = fields.Many2one("res.company","Company")

    def get_sendor(self):
        headers = {
                    'Content-Type': 'application/json',
                }
        params = {
            "fields":"first_name,last_name",
            "access_token": self.company_id.facebook_page_access_token,
        }
        url = "https://graph.facebook.com/" + str(self.sender_id) 
        r = requests.get(url, params=params)
        if r.status_code == 200:
            resp = r.text
            res = json.loads(resp)
            name = str(res['first_name'] ) +" "+ str(res['last_name'])
            self.sender_name = name
        else:
            raise Warning(r.text)

    
class FacebookMessageLine(models.Model):
    _name = 'facebook.message.line'
    _description = 'Facebook Message Line'
    
    text_message = fields.Text("Text message")
    file_message = fields.Binary("Binary message")
    file_message_type = fields.Text("File Message type")
    file_message_link = fields.Char("Link")
    date_recieved = fields.Datetime("Date Received")
    date_sent = fields.Datetime("Date Sent")
    message_seq = fields.Text("MEssage indentifier")
    
    message_type= fields.Selection([('incoming','Incoming'),
                                    ('outgoing','Outgoing')],string="Message type")
    
    message_id = fields.Many2one("facebook.message",string="Facebook Message")
        
    