import logging
import base64

from odoo import http
from odoo.http import request
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class ProductImageAccess(http.Controller):
    @http.route(["/product/image/access/<string:model>/<int:id>/<string:field>"], type='http', auth='public', website=True)
    def product_image_access(self, model='ir.attachment', field='datas', id=None):
        status, headers, content = request.env['ir.http'].sudo().binary_content(
            model=model, field=field, id=id)
        if status != 200:
            return request.env['ir.http']._response_by_status(status, headers, content)
        else:
            content_base64 = base64.b64decode(content)
            headers.append(('Content-Length', len(content_base64)))
            response = request.make_response(content_base64, headers)
            return response