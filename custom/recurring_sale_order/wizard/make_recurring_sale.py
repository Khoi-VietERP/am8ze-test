# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class RecurringSale(models.TransientModel):
	_name = 'recurring.sale'
	_description = "Recurring Sale"

	name = fields.Char('Name', related='sale_id.name')
	sale_id = fields.Many2one('sale.order', readonly=True, copy=False)
	partner_id = fields.Many2one('res.partner',string='Partner', default=lambda self: self.env.user.partner_id.id)
	first_date = fields.Datetime('Start Date', default=fields.Datetime.now)
	recurring_interval = fields.Integer('Recurring Interval',default=1)
	interval_type = fields.Selection([('days', 'Days'),
									 ('weeks', 'Weeks'),
									 ('months', 'Months')], default='days')
	recurring_number = fields.Integer('Number of Calls for Recurring',default=1)
	reviewer_ids = fields.Many2one('res.users', "Observer", default=lambda self: self.env.user, required=True,
								   readonly=True)

	
	@api.model
	def default_get(self,fields):
		res = super(RecurringSale, self).default_get(fields)
		sale_id = self.env['sale.order'].browse(self._context.get('active_id'))

		res['sale_id'] = sale_id.id
		res['partner_id'] = sale_id.partner_id.id
		return res


	@api.onchange('recurring_number','recurring_interval')
	def check_recurring_number(self):
		if self.recurring_number <= 0 or self.recurring_interval <=0:
			raise ValidationError('Please enter valid Number of Recurring Sale & Recurring Sale Interval...!')


	def confirm_recurring(self):
		first_date = self.first_date
		sale_id = self.env['sale.order'].browse(self._context.get('active_id'))
		recurring_sale_id = self.env['recurring.sales']
		if self.interval_type == 'days':
			firstdate = first_date.date()
			terms = []
			list_date = []
			list_date.append(firstdate)
			interval = self.recurring_interval
			for num in range(0,self.recurring_number):
				date = firstdate + timedelta(interval)
				interval += self.recurring_interval
				list_date.append(date)
				terms.append((0, 0, {
								'schedule_date': list_date[num],
								'name' : self.sale_id.name,
								}))
				
			new_record = self.env['recurring.sales'].create({
				'name':self.sale_id.name,
				'partner_id':self.partner_id.id,
				'interval_type':self.interval_type,
				'first_date': first_date,
				'recurring_interval':self.recurring_interval,
				'recurring_number':self.recurring_number,
				'state':'running',
				'scheduled_idss': terms,
				'sale_id': sale_id.id,
			})
			recurring_sale_id = new_record

		if self.interval_type == 'weeks':
			firstdate = first_date.date()
			terms = []
			list_date = []
			list_date.append(firstdate)
			interval = self.recurring_interval 
			for num in range(0,self.recurring_number):
				date = firstdate + timedelta(interval*7)
				interval += self.recurring_interval
				list_date.append(date)
				terms.append((0, 0, {
								'schedule_date': list_date[num],
								'name' : self.sale_id.name,
								}))

			new_record = self.env['recurring.sales'].create({
				'name':self.sale_id.name,
				'partner_id':self.partner_id.id,
				'interval_type':self.interval_type,
				'first_date':first_date,
				'recurring_interval':self.recurring_interval,
				'recurring_number':self.recurring_number,
				'state':'running',
				'scheduled_idss': terms,
				'sale_id': sale_id.id,
			})
			recurring_sale_id = new_record

		if self.interval_type == 'months':
			firstdate = first_date.date()
			terms = []
			list_date = []
			list_date.append(firstdate) 
			months = self.recurring_interval
			for num in range(0,self.recurring_number):
				date = firstdate + relativedelta(months=months)
				months += self.recurring_interval
				list_date.append(date)
				terms.append((0, 0, {
								'schedule_date': list_date[num],
								'name' : self.sale_id.name,
								}))

			new_record = self.env['recurring.sales'].create({
				'name':self.sale_id.name,
				'partner_id':self.partner_id.id,
				'interval_type':self.interval_type,
				'first_date': first_date,
				'recurring_interval':self.recurring_interval,
				'recurring_number':self.recurring_number,
				'state':'running',
				'scheduled_idss': terms,
				'sale_id': sale_id.id,
			})
			recurring_sale_id = new_record


		Cron = self.env['ir.cron']
		order_model = self.env.ref('recurring_sale_order.model_recurring_sale').id
		vals = {
			'name': self.sale_id.name,
			'model_id': order_model,
			'interval_number':self.recurring_interval,
			'interval_type': self.interval_type,
			'numbercall':self.recurring_number,
			'nextcall': first_date,
			'priority': 6,
			'user_id': self.reviewer_ids.id,
			'state': 'code',
			'code': 'model.valide_process('+str(recurring_sale_id.id)+')'
		}
		ir_cron = Cron.create(vals)
		if ir_cron:
			recurring_sale_id.update({'cron_id': ir_cron.id, 'state': 'running'})


	def valide_process(self, rec_id):
		recurring_sale_id = self.env['recurring.sales'].browse(rec_id)
		remaining = recurring_sale_id.cron_id.numbercall

		default = {'state':'draft'}
		state = 'running'
		# the recurring is over and we mark it as being done
		if remaining == 1:
			state = 'done'

		sale_id = recurring_sale_id.sale_id
		new_sale = sale_id.copy(default=default)
		self.env['sale.details'].create({
			'sale_id':new_sale.id,
			'date': recurring_sale_id.cron_id.nextcall,
			'recurring_sale_id':recurring_sale_id.id,
			'total_amount':new_sale.amount_total
		})
		recurring_sale_id.state = state

	def _cron_recurring_sale_alerts(self):
		current_date = fields.Date.today().strftime('%Y-%m-%d')
		recurring_sale_ids = self.env['recurring.sales'].search([('state','=','running')])
		for recurring_sale_id in recurring_sale_ids:
			if recurring_sale_id.scheduled_idss:
				schedule_date_lst = []
				for sched in recurring_sale_id.scheduled_idss:
					schedule_date = sched.schedule_date - timedelta(days=1)
					schedule_date = schedule_date.strftime('%Y-%m-%d')
					schedule_date_lst.append(schedule_date)
				if current_date in schedule_date_lst:
					template_id =  self.env.ref('recurring_sale_order.recurring_sale_remainder_template')
					values = template_id.generate_email(self.id, fields=None)
					values['email_from'] = self.env.user.email_formatted
					values['email_to'] = recurring_sale_id.partner_id.email
					values['author_id'] = self.env.user.partner_id.id
					values['subject'] = 'Reminder Mail for Recurring Sale Order'
					main_body = """<p> Dear %s , <br/><br/>
									This is a Reminder Mail For Your Recurring Sale Order:<br/><br/>
									Regards,<br/>
									%s </p>
										 """%(recurring_sale_id.partner_id.name, self.env.user.name)
					values['body_html'] = main_body
					mail_mail_obj = self.env['mail.mail']
					msg_id = mail_mail_obj.sudo().create(values)
					if msg_id:
						msg_id.sudo().send()
