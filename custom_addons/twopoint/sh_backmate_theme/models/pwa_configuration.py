# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, fields, models, _, tools
from odoo.modules.module import get_resource_path
import base64

mime_selection = [ ('image/png', 'image/png'),('image/x-icon', 'image/x-icon'), ('image/gif', 'image/gif')]
display_selection = [('fullscreen', 'Fullscreen'), ('standalone', 'Standalone'), ('minimal-ui', 'Minimal')]
orientation_selection = [('landscape', 'Always Landscape')]

class PWAConfig(models.Model):
    _name = 'sh.pwa.config'
    _description = 'PWA Configuration'

    def _default_icon_small(self):
        image_path = get_resource_path('sh_backmate_theme', 'static/icon', 'small_am8ze_icon.png')
        with tools.file_open(image_path, 'rb') as f:
            return base64.b64encode(f.read())

    def _default_icon(self):
        image_path = get_resource_path('sh_backmate_theme', 'static/icon', 'am8ze_icon.png')
        with tools.file_open(image_path, 'rb') as f:
            return base64.b64encode(f.read())

    name = fields.Char(required=True, default='Softhealer')
    short_name = fields.Char(required=True, default='Softhealer')
    theme_color = fields.Char(default='#DBDCDE')
    background_color = fields.Char(default='#3367D6')
    display = fields.Selection(selection=display_selection, default='fullscreen', required=True)
    orientation = fields.Selection(selection=orientation_selection)
    icon_small = fields.Binary(help='Set a small app icon. Must be at least 32x32 pixels', default=_default_icon_small)
    icon_small_mimetype = fields.Selection(selection=mime_selection, help='Set the mimetype of your small icon.', default='image/png')
    icon_small_size = fields.Char(default='32x32')
    icon = fields.Binary(help='Set a big app icon. Must be at least 512x512 pixels', default=_default_icon)
    icon_mimetype = fields.Selection(selection=mime_selection, help='Set the mimetype of your icon.', default='image/png')
    icon_size = fields.Char(default='512x512')
    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.user.company_id.id)
    icon_iphone = fields.Binary(help='Icon for Iphone',string="Icon for Iphone", default=_default_icon)
#     @api.model
#     def default_get(self,default_fields):
#         """ 
#             Get Default Settings.
#              
#         """
#         res = super(PWAConfig, self).default_get(default_fields)
#          
#         record = self.search_read([
#             ('name','=','sh_pwa_backend_config')
#             ],limit = 1, order="id desc")
#         
#          
#         if record:
#             res.update(record[0])
#                   
#         return res
