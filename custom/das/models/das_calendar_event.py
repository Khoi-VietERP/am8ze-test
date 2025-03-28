# -*- coding: utf-8 -*-

from odoo import models, fields, api

class calendar_event(models.Model):
    _inherit = 'calendar.event'

    state = fields.Selection([('schedule', 'Schedule'), ('approval', 'Approval'), ('completed', 'Completed'), ('cancel', 'Cancel')], default='schedule', readonly=1)
    warehouse_id = fields.Many2one('stock.warehouse', string="Location")
    direction = fields.Selection([('incoming', 'Incoming'),('outgoing', 'Outgoing')], string="Direction")
    cases = fields.Char(string="Cases")
    pallets = fields.Char(string="Pallets")
    units = fields.Char(string="Units")
    pallet_type_id = fields.Many2one('pallet.type', string="Pallet Type")
    carrier_id = fields.Many2one('res.partner', string="Carrier")
    carrier_type_id = fields.Many2one('das.carrier.type', string="Carrier Type")
    carrier_number = fields.Char(string="Carrier Number")
    po_number = fields.Many2one('purchase.order',string="PO Number")
    driver = fields.Char(string="Driver")
    priority = fields.Boolean(string="Priority")
    docking_location_id = fields.Many2one('stock.location', string="Docking Location")
    actual_start_date_time = fields.Datetime(string="Actual Start Date /Time", readonly=1)
    actual_end_date_time = fields.Datetime(string="Actual End Date /Time", readonly=1)
    checkin_date_time = fields.Datetime(string="Check in Date /Time", readonly=1)
    checkout_date_time = fields.Datetime(string="Check out Date /Time", readonly=1)
    das_calendar_document_ids = fields.One2many('das.calendar.document', 'event_id')
    picking_count = fields.Integer(compute='_compute_picking', string='Picking count', default=0)
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking', string='Receptions')


    @api.model
    def create(self, values):
        res = super(calendar_event, self).create(values)
        res.name = self.env['ir.sequence'].next_by_code('calendar.event')
        return res

    def approval(self):
        self.write({
            'state' : 'approval'
        })

    def cancel(self):
        self.write({
            'state': 'cancel'
        })

    def action_start(self):
        self.write({
            'actual_start_date_time' : fields.Datetime.now()
        })

    def completed(self):
        self.write({
            'actual_end_date_time' : fields.Datetime.now(),
            'state' : 'completed'
        })

    def action_checkin(self):
        self.write({
            'checkin_date_time': fields.Datetime.now()
        })

    def action_checkout(self):
        self.write({
            'checkout_date_time': fields.Datetime.now()
        })

    def _compute_picking(self):
        for rec in self:
            rec.picking_count = rec.po_number.picking_count
            rec.picking_ids = rec.po_number.picking_ids

    def action_view_picking(self):
        """ This function returns an action that display existing picking orders of given purchase order ids. When only one found, show the picking immediately.
        """
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]
        # override the context to get rid of the default filtering on operation type
        result['context'] = {'default_partner_id': self.po_number.partner_id.id, 'default_origin': self.po_number.name, 'default_picking_type_id': self.po_number.picking_type_id.id}
        pick_ids = self.mapped('picking_ids')
        # choose the view_mode accordingly
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = pick_ids.id
        return result

class pallet_type(models.Model):
    _name = 'pallet.type'

    name = fields.Char(string='Name')

class das_carrier(models.Model):
    _name = 'das.carrier'

    name = fields.Char(string='Name')

class das_carrier_type(models.Model):
    _name = 'das.carrier.type'

    name = fields.Char(string='Name')

class das_calendar_document(models.Model):
    _name = 'das.calendar.document'

    document_type_id = fields.Many2one('das.calendar.document.type', string='Document Type')
    document_number = fields.Char(string="Document number")
    attachment = fields.Binary("Add atttachment", attachment=True)
    event_id = fields.Many2one('calendar.event')

class das_calendar_document_type(models.Model):
    _name = 'das.calendar.document.type'

    name = fields.Char(string='Name')

class das_calendar_warehouse(models.Model):
    _name = 'das.calendar.warehouse'
    _description = 'Calendar warehouse'

    user_id = fields.Many2one('res.users', 'Me', required=True, default=lambda self: self.env.user)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', required=True)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('user_id_warehouse_id_unique', 'UNIQUE(user_id,warehouse_id)', 'An user cannot have twice the same warehouse.')
    ]

    @api.model
    def unlink_from_warehouse_id(self, warehouse_id):
        return self.search([('warehouse_id', '=', warehouse_id)]).unlink()


