from odoo import models, fields


class DatapostReceiveResponse(models.Model):
    _name = 'datapost.received.response'
    _description = 'Datapost Receive Response'

    peppol_document_no = fields.Char('Peppol Document No', required=True)
    move_id = fields.Many2one('account.move')
    purchase_id = fields.Many2one('purchase.order')
    response_code = fields.Selection([
        ('AB', 'Message acknowledgement'),
        ('IP', 'In Progress'),
        ('UQ', 'Under Query'),
        ('RE', 'Rejected'),
        ('AP', 'Accepted'),
        ('CA', 'Conditionally Accepted'),
        ('PD', 'Fully Paid'),
        ('NOA', 'Not Applicable'),
    ], string='Response Code', required=True)
    effective_date = fields.Char('Effective Date')
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
    response_reason = fields.Char('Response Reason')
