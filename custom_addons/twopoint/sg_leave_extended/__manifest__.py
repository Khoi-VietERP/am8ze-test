# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    "name": "Singapore Leave Extension",
    "version": "13.0.1.0.0",
    "license": "LGPL-3",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "maintainer": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "category": "Human Resources",
    "description":
    '''
    Module to manage Leave information.
    Based on configuration detail, leave increment done through selected
    interval unit and interval unit number
    ''',
    "summary":
    '''
    Module to manage Leave information.
    ''',
    "depends": ["sg_holiday_extended"],

    "data": [
        "security/ir.model.access.csv",
        "views/sg_leave_extended_view.xml",
        ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": 99,
    "currency": 'EUR',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
