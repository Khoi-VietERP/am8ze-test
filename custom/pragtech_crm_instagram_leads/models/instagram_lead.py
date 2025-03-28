# -*- coding: utf-8 -*-

import logging
import requests

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class CrmInstagramPage(models.Model):
    _name = 'crm.instagram.page'
    _description = 'Instagram Page'
    _rec_name = 'instagram_account'
    #
    # name = fields.Char(required=True)
    # access_token = fields.Char(required=True, string='Page Access Token')

    instagram_account = fields.Many2one(
        'instagram.pragtech.social.account', string='Page Name')
    instagram_access_token = fields.Char(string="Page Access Token", related='instagram_account.instagram_access_token', store=True,
                               readonly=False, tracking=True)
    name = fields.Char(string="Page ID", related='instagram_account.instagram_account_id', required=True)

    form_ids = fields.One2many('crm.instagram.form', 'page_id', string='Lead Forms')

    def instagram_lead_form_processing(self, r):
        # print("instagram_lead_form_processing-----------------")
        if not r.get('data'):
            return

        for form in r['data']:
            if self.form_ids.filtered(
                    lambda f: f.instagram_form_id == form['id']):
                continue
            self.env['crm.instagram.form'].create({
                'name': form['name'],
                'instagram_form_id': form['id'],
                'page_id': self.id}).fetch_instagram_form_fields()

        if r.get('paging') and r['paging'].get('next'):
            self.instagram_lead_form_processing(requests.get(r['paging']['next']).json())
        return

    def fetch_instagram_forms(self):
        # print("fetch_instagram_forms==================",self)
        r = requests.get("https://graph.facebook.com/v10.0/" + self.name + "/leadgen_forms",
                         params={'access_token': self.instagram_access_token}).json()
        # print("r==============================",r)
        self.instagram_lead_form_processing(r)


class CrmInstagramForm(models.Model):
    _name = 'crm.instagram.form'
    _description = 'instagram Form Page'

    name = fields.Char(required=True)
    allow_to_sync = fields.Boolean()
    instagram_form_id = fields.Char(required=True, string='Form ID')
    instagram_access_token = fields.Char(required=True, related='page_id.instagram_access_token', string='Page Access Token')
    page_id = fields.Many2one('crm.instagram.page', readonly=True, ondelete='cascade', string='Instagram Page')
    mappings = fields.One2many('crm.instagram.form.field', 'form_id')
    team_id = fields.Many2one('crm.team', domain=['|', ('use_leads', '=', True), ('use_opportunities', '=', True)],
                              string="Sales Team")
    campaign_id = fields.Many2one('utm.campaign')
    source_id = fields.Many2one('utm.source')
    medium_id = fields.Many2one('utm.medium')
    state = fields.Selection([
        ('draft', 'Draft'), ('confirm', 'Confirm')
    ], string='State', required=True, default='draft')

    def fetch_instagram_form_fields(self):

        self.mappings.unlink()
        r = requests.get("https://graph.facebook.com/v10.0/" + self.instagram_form_id,
                         params={'access_token': self.instagram_access_token, 'fields': 'questions'}).json()
        if r.get('questions'):
            for questions in r.get('questions'):

                self.env['crm.instagram.form.field'].create({
                    'form_id': self.id,
                    'name': questions['label'],
                    'fb_field': questions['key']
                })

    def validate_instagram_form(self):
        if self.state and self.state == 'draft':
            self.state = 'confirm'
            self.allow_to_sync = True


class CrmInstagramFormField(models.Model):
    _name = 'crm.instagram.form.field'
    _description = 'Instagram form fields'

    form_id = fields.Many2one('crm.instagram.form', required=True, ondelete='cascade', string='Form')
    name = fields.Text()
    For_map_odoo_field = fields.Many2one('ir.model.fields',domain=[('model', '=', 'crm.lead'),('store', '=', True),('ttype', 'in', ('char','date','datetime','float','html',
                                                          'integer',
                                                          'monetary',
                                                          'many2one',
                                                          'selection',
                                                          'phone',
                                                          'text'))],
                                 required=False)
    fb_field = fields.Text(required=True)

    _sql_constraints = [
        ('field_unique', 'unique(form_id, For_map_odoo_field, fb_field)', 'Mapping must be unique per form')
    ]


class InstagramUtmMedium(models.Model):
    _inherit = 'utm.medium'

    instagram_ad_id = fields.Char()

    _sql_constraints = [
        ('instagram_ad_unique', 'unique(instagram_ad_id)',
         'This Instagram Ad already exists!')
    ]


class InstagramUtmAdset(models.Model):
    _name = 'utm.adset'
    _description = 'Utm Adset'

    name = fields.Char()
    instagram_adset_id = fields.Char()

    _sql_constraints = [
        ('instagram_adset_unique', 'unique(instagram_adset_id)',
         'This Instagram AdSet already exists!')
    ]


class InstagramUtmCampaign(models.Model):
    _inherit = 'utm.campaign'

    instagram_campaign_id = fields.Char()

    _sql_constraints = [
        ('instagram_campaign_unique', 'unique(instagram_campaign_id)',
         'This Instagram Campaign already exists!')
    ]


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    description = fields.Html('Notes')
    instagram_lead_id = fields.Char(readonly=True)
    instagram_page_id = fields.Many2one(
        'crm.instagram.page', related='instagram_form_id.page_id',
        store=True, readonly=True)
    instagram_form_id = fields.Many2one('crm.instagram.form', readonly=True)
    instagram_adset_id = fields.Many2one('utm.adset', readonly=True)
    instagram_ad_id = fields.Many2one(
        'utm.medium', related='medium_id', store=True, readonly=True,
        string='Instagram Ad')
    instagram_campaign_id = fields.Many2one(
        'utm.campaign', related='campaign_id', store=True, readonly=True,
        string='Instagram Campaign')
    instagram_date_create = fields.Datetime(readonly=True)
    instagram_is_organic = fields.Boolean(readonly=True)

    _sql_constraints = [
        ('instagram_lead_unique', 'unique(instagram_lead_id)',
         'This Instagram lead already exists!')
    ]

    def instagram_fetch_ad(self, lead):
        ad_obj = self.env['utm.medium']
        if not lead.get('ad_id'):
            return ad_obj
        if not ad_obj.search(
                [('instagram_ad_id', '=', lead['ad_id'])]):
            return ad_obj.create({
                'instagram_ad_id': lead['ad_id'], 'name': lead['ad_name'], }).id

        return ad_obj.search(
            [('instagram_ad_id', '=', lead['ad_id'])], limit=1)[0].id

    def instagram_fetch_adset(self, lead):
        ad_obj = self.env['utm.adset']
        if not lead.get('adset_id'):
            return ad_obj
        if not ad_obj.search(
                [('instagram_adset_id', '=', lead['adset_id'])]):
            return ad_obj.create({
                'instagram_adset_id': lead['adset_id'], 'name': lead['adset_name'], }).id

        return ad_obj.search(
            [('instagram_adset_id', '=', lead['adset_id'])], limit=1)[0].id

    def instagram_fetch_campaign(self, lead):
        campaign_instance = self.env['utm.campaign']
        if not lead.get('campaign_id'):
            return campaign_instance
        if not campaign_instance.search(
                [('instagram_campaign_id', '=', lead['campaign_id'])]):
            return campaign_instance.create({
                'instagram_campaign_id': lead['campaign_id'],
                'name': lead['campaign_name'], }).id

        return campaign_instance.search(
            [('instagram_campaign_id', '=', lead['campaign_id'])],
            limit=1)[0].id

    def instagram_generate_lead_creation(self, lead, form):
        vals, notes = self.instagarm_fetch_fields_from_data(lead, form)
        # if not vals.get('email_from') and lead.get('email'):
        #     vals['email_from'] = lead['email']
        # if not vals.get('contact_name') and lead.get('full_name'):
        #     vals['contact_name'] = lead['full_name']
        # if not vals.get('phone') and lead.get('phone_number'):
        #     vals['phone'] = lead['phone_number']

        source_id = self.env.ref('pragtech_crm_instagram_leads.utm_source_instagram')
        medium_id = self.env.ref('pragtech_crm_instagram_leads.utm_medium_instagram')
        # coming_fb_lead_name = ''
        # if 'full_name' in lead:
        #     coming_fb_lead_name = lead['full_name']
        # else:
        #     coming_fb_lead_name = lead['FULL_NAME']

        vals.update({
            'instagram_lead_id': lead['id'],
            'instagram_is_organic': lead['is_organic'],
            'name': self.instagram_fetch_opportunity_name(vals, lead, form),
            'description': "\n".join(notes),
            'team_id': form.team_id and form.team_id.id,
            'campaign_id': form.campaign_id and form.campaign_id.id or
                           self.instagram_fetch_campaign(lead),
            'source_id': source_id.id,
            'medium_id': medium_id.id,
            'user_id': form.team_id and form.team_id.user_id and form.team_id.user_id.id or False,
            'instagram_adset_id': self.instagram_fetch_adset(lead),
            'instagram_form_id': form.id,
            'instagram_date_create': lead['created_time'].split('+')[0].replace('T', ' ')
        })
        return vals

    def instagram_lead_generation(self, lead, form):
        vals = self.instagram_generate_lead_creation(lead, form)
        # print("vals==================",vals)
        lead_created = self.create(vals)
        # print("lead_created=======================",lead_created)
        return lead_created

    def instagram_fetch_opportunity_name(self, vals, lead, form):
        if not vals.get('name'):
            vals['name'] = '%s - %s' % (form.name, lead['id'])
        return vals['name']

    def instagarm_fetch_fields_from_data(self, lead, form):
        # print("\n\n\n=======fetch_fields_from_data==============",self)
        vals, notes = {}, []
        form_mapping = form.mappings.filtered(lambda m: m.For_map_odoo_field).mapped('fb_field')
        # print("form_mapping=================",form.mappings.filtered(lambda m: m.fb_field))

        unmapped_fields = []
        for name, value in lead.items():
            if name not in form_mapping:
                unmapped_fields.append((name, value))
                # print("unmapped_fieldsssssss===============",name)
                continue
            For_map_odoo_field = form.mappings.filtered(lambda m: m.fb_field == name).For_map_odoo_field
            # print("For_map_odoo_field=============ggggggggggggggggggggggggggggggggggggggggggg",For_map_odoo_field)
            # notes.append('<b>%s</b>: %s <br><br>' % ((For_map_odoo_field.field_description).capitalize().replace("_", " "), value))
            if For_map_odoo_field.ttype == 'many2one':
                related_value = self.env[For_map_odoo_field.relation].search([('display_name', '=', value)])
                vals.update({For_map_odoo_field.name: related_value and related_value.id})
            elif For_map_odoo_field.ttype in ('float', 'monetary'):
                vals.update({For_map_odoo_field.name: float(value)})
            elif For_map_odoo_field.ttype == 'integer':
                vals.update({For_map_odoo_field.name: int(value)})
            # TODO: separate date & datetime into two different conditionals
            elif For_map_odoo_field.ttype in ('date', 'datetime'):
                vals.update({For_map_odoo_field.name: value.split('+')[0].replace('T', ' ')})
            elif For_map_odoo_field.ttype == 'selection':
                vals.update({For_map_odoo_field.name: value})
            elif For_map_odoo_field.ttype == 'boolean':
                vals.update({For_map_odoo_field.name: value == 'true' if value else False})
            else:
                vals.update({For_map_odoo_field.name: value})

        # NOTE: Doing this to put unmapped fields at the end of the description
        for name, value in unmapped_fields:
            # print("name==============",type(name))
            if name not in ['created_time','is_organic','id']:
                notes.append('<b>%s</b>: %s <br><br>' % (str(name.capitalize().replace("_", " ")), value))

        return vals, notes

    def instagram_execute_lead_field_data(self, lead):
        # print("instagram_execute_lead_field_data================",lead)
        field_data = lead.pop('field_data')
        lead_data = dict(lead)
        lead_data.update([(l['name'], l['values'][0])
                          for l in field_data
                          if l.get('name') and l.get('values')])
        return lead_data

    def instagram_lead_execution(self, r, form):
        # print("instagram_lead_execution============",r,form)
        if not r.get('data'):
            return
        for lead in r['data']:
            lead = self.instagram_execute_lead_field_data(lead)
            # print("lead================",lead)
            if not self.search(
                    [('instagram_lead_id', '=', lead.get('id')), '|', ('active', '=', True), ('active', '=', False)]):
                test1=self.instagram_lead_generation(lead, form)
                # print("test1===========================",test1)

        # /!\ NOTE: Once finished a page let us commit that
        try:
            self.env.cr.commit()
        except Exception:
            self.env.cr.rollback()

        if r.get('paging') and r['paging'].get('next'):
            _logger.info('Fetching a new page in Form: %s' % form.name)
            self.instagram_lead_execution(requests.get(r['paging']['next']).json(), form)
        return

    @api.model
    def instagarm_fetch_instagarm_leads(self):
        # print("instagarm_fetch_instagarm_leads===============",self)
        # /!\ TODO: Add this URL as a configuration setting in the company
        insta_api = "https://graph.facebook.com/v10.0/"
        for form in self.env['crm.instagram.form'].search([('state', '=', 'confirm')]):
            # print("form===============",form)
            # /!\ NOTE: We have to try lead creation if it fails we just log it into the Lead Form?
            _logger.info('Starting to fetch leads from Form: %s' % form.name)
            r = requests.get(insta_api + form.instagram_form_id + "/leads", params={'access_token': form.instagram_access_token,
                                                                                'fields': 'created_time,field_data,ad_id,ad_name,adset_id,adset_name,campaign_id,campaign_name,is_organic'}).json()

            # print('\n\n\n instagarm_fetch_facebook_leads ==>>> ', r)
            self.instagram_lead_execution(r, form)
        _logger.info('Fetch of leads has ended')
