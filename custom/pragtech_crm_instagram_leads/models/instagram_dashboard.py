from odoo import fields, models, _

class InstagramSocailDashboard(models.Model):
    _name = "instagram.socail.dashboard"
    _description = "Instagram Dashboard"

    name = fields.Char()

