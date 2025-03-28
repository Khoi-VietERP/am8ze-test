# -*- coding: utf-8 -*-

from odoo import models, api
from reportlab.graphics.barcode import createBarcodeDrawing


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def barcode(self, barcode_type, value, width=600, height=100, humanreadable=0, quiet=1):
        if barcode_type == 'UPCA' and len(value) in (11, 12, 13):
            barcode_type = 'EAN13'
            if len(value) in (11, 12):
                value = '0%s' % value
        elif barcode_type == 'auto':
            symbology_guess = {8: 'EAN8', 13: 'EAN13'}
            barcode_type = symbology_guess.get(len(value), 'Code128')
        try:
            width, height, humanreadable, quiet = int(width), int(height), bool(int(humanreadable)), bool(int(quiet))
            # for `QR` type, `quiet` is not supported. And is simply ignored.
            # But we can use `barBorder` to get a similar behaviour.
            bar_border = 4
            if barcode_type == 'QR' and quiet:
                bar_border = 0

            checksum = 1
            if barcode_type == 'Standard39':
                checksum = 0

            barcode = createBarcodeDrawing(
                barcode_type, value=value, format='png', width=width, height=height,
                humanReadable=humanreadable, quiet=quiet, barBorder=bar_border, checksum=checksum
            )
            return barcode.asString('png')
        except (ValueError, AttributeError):
            if barcode_type == 'Code128':
                raise ValueError("Cannot convert into barcode.")
            else:
                return self.barcode('Code128', value, width=width, height=height,
                    humanreadable=humanreadable, quiet=quiet)