import json
import base64
import logging

from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.tools.misc import str2bool

_logger = logging.getLogger(__name__)


class BulkExpenseController(http.Controller):

    @http.route('/bulk_expense/attachment/add', type='http', auth="user", methods=['POST'])
    def bulk_expense_add_attachment(self, ufile, record=None, temporary=False, **kw):
        try:
            name = ufile.filename
            request.env['bulk.expense.line'].create({
                'attachment_name': name,
                'attachment_id': base64.b64encode(ufile.read()),
                'bulk_expense_id' : int(record)
            })
        except:
            pass
