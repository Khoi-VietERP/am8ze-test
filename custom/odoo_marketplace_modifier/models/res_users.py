# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def signup(self, values, token=None):
        """ """
        context = dict(self._context)
        is_seller = values.get('is_seller') or context.get('is_seller')
        if is_seller:
            context['mobile_no'] = values.get('mobile_no')
            values.pop("mobile_no")

            context['company_address'] = values.get('company_address')
            values.pop("company_address")

            context['street2'] = values.get('street2')
            values.pop("street2")

            context['postal_code'] = values.get('postal_code')
            values.pop("postal_code")

            context['membership_state'] = values.get('membership_state')
            values.pop("membership_state")

            context['uen'] = values.get('uen')
            values.pop("uen")

            context['name_of_ao'] = values.get('name_of_ao')
            values.pop("name_of_ao")

            context['official_designation'] = values.get('official_designation')
            values.pop("official_designation")

            context['date_of_acti'] = values.get('date_of_acti')
            values.pop("date_of_acti")

            context['comment'] = values.get('comment')
            values.pop("comment")

            context['receive_update'] = values.get('receive_update')
            values.pop("receive_update")

        is_cust = values.get('is_cust') or context.get('is_cust')
        if is_cust:
            context['is_cust'] = values.get('is_cust')
            values.pop("is_cust")

            context['mobile_no'] = values.get('mobile_no')
            values.pop("mobile_no")

            context['company_name'] = values.get('company_name')
            values.pop("company_name")

            context['uen'] = values.get('uen')
            values.pop("uen")

            context['staff_strength'] = values.get('staff_strength')
            values.pop("staff_strength")

            context['industry_sector_id'] = values.get('industry_sector_id')
            values.pop("industry_sector_id")

            context['officical_designation'] = values.get('officical_designation')
            values.pop("officical_designation")

            context['receive_update'] = values.get('receive_update')
            values.pop("receive_update")

            context['remarks'] = values.get('remarks')
            values.pop("remarks")

        return super(ResUsers, self.with_context(context)).signup(values, token)


    def copy(self, default=None):
        self.ensure_one()
        user_obj = super(ResUsers, self).copy(default=default)
        if self._context.get('is_seller', False):

            wk_valse = {
                'mobile' : self._context.get('mobile_no', False),
                'street' : self._context.get('company_address', False),
                'street2' : self._context.get('street2', False),
                'zip' : self._context.get('postal_code', False),
                'membership_state' : self._context.get('membership_state', False),
                'uen' : self._context.get('uen', False),
                'name_au_officer' : self._context.get('name_of_ao', False),
                'officical_designation' : self._context.get('official_designation', False),
                'date_of_activation' : self._context.get('date_of_acti', False),
                'remarks' : self._context.get('comment', False),
                'receive_update' : self._context.get('receive_update', False),
            }
            user_obj.partner_id.write(wk_valse)

        if self._context.get('is_cust', False):
            wk_valse = {
                'customer_rank' : 1,
                'mobile': self._context.get('mobile_no', False),
                'company_name': self._context.get('company_name', False),
                'uen': self._context.get('uen', False),
                'staff_strength_id': int(self._context.get('staff_strength', False)) if self._context.get('staff_strength', False) else False,
                'industry_sector_id': int(self._context.get('industry_sector_id', False)) if self._context.get('industry_sector_id', False) else False,
                'function': self._context.get('officical_designation', False),
                'receive_update': self._context.get('receive_update', False),
                'remarks': self._context.get('remarks', False),
            }

            user_obj.partner_id.write(wk_valse)

            if user_obj.partner_id.company_name:
                user_obj.partner_id.create_company()
                user_obj.partner_id.company_type = 'company'
        return user_obj