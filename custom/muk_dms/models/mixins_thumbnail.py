###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Documents 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import os
import json
import base64
import operator
import functools
import collections

from odoo import models, fields, api, tools
from odoo.modules.module import get_resource_path

class Thumbnail(models.AbstractModel):
    
    _name = 'muk_dms.mixins.thumbnail'
    _description = 'Thumbnail Mixin'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    custom_thumbnail = fields.Binary(
        string="Custom Thumbnail")
     
    custom_thumbnail_medium = fields.Binary(
        string="Medium Custom Thumbnail")
     
    custom_thumbnail_small = fields.Binary(
        string="Small Custom Thumbnail")
     
    thumbnail = fields.Binary(
        compute='_compute_thumbnail',
        string="Thumbnail")
 
    thumbnail_medium = fields.Binary(
        compute='_compute_thumbnail_medium',
        string="Medium Thumbnail")
     
    thumbnail_small = fields.Binary(
        compute='_compute_thumbnail_small',
        string="Small Thumbnail")

    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    @api.model
    def _get_thumbnail_placeholder(self, field, size, name):
        if self._check_context_bin_size(field):
            return self._get_thumbnail_placeholder_size(size, name)
        else:
            return self._get_thumbnail_placeholder_image(size, name)
    
    @api.model
    def _get_thumbnail_placeholder_image(self, size, name):
        path = self._get_thumbnail_path(size, name)
        with open(path, "rb") as image:
            return base64.b64encode(image.read())
    
    @api.model
    def _get_thumbnail_placeholder_size(self, size, name):
        return os.path.getsize(self._get_thumbnail_path(size, name))
    
    @api.model
    def _get_thumbnail_path(self, size, name):
        folders = ['static', 'src', 'img', 'thumbnails']
        path = get_resource_path('muk_dms', *folders, name)
        if not os.path.isfile(path):
            path = get_resource_path('muk_dms', *folders, "file_unkown.svg")
        return path
    
    
    def _get_thumbnail_placeholder_name(self):
        return "folder.svg"
    
    #----------------------------------------------------------
    # Read 
    #----------------------------------------------------------
    
    @api.depends('custom_thumbnail')
    def _compute_thumbnail(self):
        for record in self:
            if record.custom_thumbnail:
                record.thumbnail = record.custom_thumbnail        
            else:
                record.thumbnail = self._get_thumbnail_placeholder(
                    'thumbnail', 'original', record._get_thumbnail_placeholder_name()
                )
     
    @api.depends('custom_thumbnail_medium')
    def _compute_thumbnail_medium(self):
        for record in self:
            if record.custom_thumbnail_medium:
                record.thumbnail_medium = record.custom_thumbnail_medium        
            else:
                record.thumbnail_medium = self._get_thumbnail_placeholder(
                    'thumbnail_medium', 'medium', record._get_thumbnail_placeholder_name()
                )
     
    @api.depends('custom_thumbnail_small')
    def _compute_thumbnail_small(self):
        for record in self:
            if record.custom_thumbnail_small:
                record.thumbnail_small = record.custom_thumbnail_small     
            else:
                record.thumbnail_small = self._get_thumbnail_placeholder(
                    'thumbnail_small', 'small', record._get_thumbnail_placeholder_name()
                )
    
    #----------------------------------------------------------
    # Create, Update, Delete
    #----------------------------------------------------------
    def image_resize_image(self, image, x, y):
        image = tools.ImageProcess(image)
        image.resize(x, y)
        resize_image_b64 = image.image_base64()
        return resize_image_b64

    @api.model
    def create(self, vals_list):
        if 'custom_thumbnail' in vals_list:
            custom_thumbnail = self.image_resize_image(vals_list['custom_thumbnail'],1024,1024)
            vals_list.update({
                'custom_thumbnail' : custom_thumbnail
            })
        if 'custom_thumbnail_medium' in vals_list:
            custom_thumbnail_medium = self.image_resize_image(vals_list['custom_thumbnail_medium'],128,128)
            vals_list.update({
                'custom_thumbnail_medium' : custom_thumbnail_medium
            })
        if 'custom_thumbnail_small' in vals_list:
            custom_thumbnail_small = self.image_resize_image(vals_list['custom_thumbnail_small'],64,64)
            vals_list.update({
                'custom_thumbnail_small' : custom_thumbnail_small
            })

        return super(Thumbnail, self).create(vals_list)


    def write(self, vals):
        if 'custom_thumbnail' in vals:
            custom_thumbnail = self.image_resize_image(vals['custom_thumbnail'], 1024, 1024)
            vals.update({
                'custom_thumbnail': custom_thumbnail
            })
        if 'custom_thumbnail_medium' in vals:
            custom_thumbnail_medium = self.image_resize_image(vals['custom_thumbnail_medium'], 128, 128)
            vals.update({
                'custom_thumbnail_medium': custom_thumbnail_medium
            })
        if 'custom_thumbnail_small' in vals:
            custom_thumbnail_small = self.image_resize_image(vals['custom_thumbnail_small'], 64, 64)
            vals.update({
                'custom_thumbnail_small': custom_thumbnail_small
            })
        return super(Thumbnail, self).write(vals)
            