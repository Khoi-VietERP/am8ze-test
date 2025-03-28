# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class DatapostResponseCode(models.TransientModel):
    _name = 'datapost.response.code'

    name = fields.Text('')
    document_type = fields.Selection([
        ('invoice-response', 'Invoice'),
        ('order-response', 'Order'),
    ], string='Document Type', default="invoice-response", required=True)
    response_code = fields.Selection([
        ('AB', 'Message acknowledgement'),
        ('IP', 'In Progress'),
        ('UQ', 'Under Query'),
        ('RE', 'Rejected'),
        ('AP', 'Accepted'),
        ('CA', 'Conditionally Accepted'),
        # ('PPD', 'Partially Paid'),
        ('PD', 'Fully Paid'),
    ], string='Response Code', required=True)
    response_reason_code = fields.Selection([
        ('NON', 'No Issue'),
        ('REF', 'References incorrect'),
        ('LEG', 'Legal information incorrect'),
        ('REC', 'Receiver unknown'),
        ('QUA', 'Item quality insufficient'),
        ('DEL', 'Delivery issues'),
        ('PRI', 'Prices incorrect'),
        ('QTY', 'Quantity incorrect'),
        ('ITM', 'Items incorrect'),
        ('PAY', 'Payment terms incorrect'),
        ('UNR', 'Not recognized'),
        ('FIN', 'Finance incorrect'),
        ('PPD', 'Partially Paid'),
        ('OTH', 'Other'),
    ])
    response_reason = fields.Text('Response Reason')
    move_id = fields.Many2one('account.move')
    sale_id = fields.Many2one('sale.order')

    def action_send_response(self):
        self.ensure_one()

        api_id = self.env['datapost.api'].search([], limit=1)
        datapost_response_id = self.env['datapost.response'].create({
            'document_type': self.document_type,
            'move_id': self.move_id.id,
            'sale_id': self.sale_id.id,
            'response_code': self.response_code,
            'response_reason': self.response_reason,
            'response_reason_code': self.response_reason_code,
            'api_id': api_id.id,
        })
        datapost_response_id.action_send_document()
