
import pytz
import math
import time
import calendar
from dateutil import parser, rrule
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import odoo.tools as tools
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DSDTF,\
    DEFAULT_SERVER_DATE_FORMAT as DSDF


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    branch_id = fields.Char("Branch ID")


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    id = fields.Integer('ID', readonly=True)

    def _compute_rule(self, localdict):
        if localdict is None or not localdict:
            localdict = {}
        localdict.update({'math': math})
        return super(HrSalaryRule, self)._compute_rule(localdict)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.depends('date_from', 'date_to', 'employee_id', 'employee_id.user_id')
    def _get_total_public_holiday_hours(self):
        holiday_line_obj = self.env['hr.holiday.lines']
        analytic_line_obj = self.env['account.analytic.line']
        self.pub_holiday_hours = 0.0
        for payslip in self:
            domain = [('holiday_date', '>=', payslip.date_from),
                      ('holiday_date', '<=', payslip.date_to),
                      ('holiday_id.state', '=', 'validated')]
            public_holi_ids = holiday_line_obj.search(domain)
            pub_holi_days = []
            for line in public_holi_ids:
                pub_holi_days.append(line.holiday_date)
            total_hours = 0.0
            if payslip.employee_id.user_id:
                domain = [('user_id', '=', payslip.employee_id.user_id.id),
                          ('date', '>=', payslip.date_from),
                          ('date', '<=', payslip.date_to),
                          ('date', 'in', pub_holi_days)]
                account_analytic_search_ids = analytic_line_obj.search(domain)
                if account_analytic_search_ids:
                    for timesheet in account_analytic_search_ids:
                        total_hours = total_hours + timesheet.unit_amount \
                            or 0.0
                        payslip.pub_holiday_hours = total_hours

    @api.depends('employee_id.user_id', 'date_from', 'date_to', 'employee_id')
    def _get_total_hours(self):
        analytic_line_obj = self.env['account.analytic.line']
        self.total_timesheet_hours = self.total_hours = \
            self.overtime_hours = 0.0
        for payslip in self:
            total_timesheet_hours = 0.0
            if payslip.employee_id.user_id:
                domain = [('user_id', '=', payslip.employee_id.user_id.id),
                          ('date', '>=', payslip.date_from),
                          ('date', '<=', payslip.date_to)]
                account_analytic_search_ids = analytic_line_obj.search(domain)
                for timesheet in account_analytic_search_ids:
                    total_timesheet_hours += timesheet.unit_amount or 0.0
                    payslip.total_timesheet_hours = total_timesheet_hours
            payslip.total_hours = 0.0
            for work_days in payslip.worked_days_line_ids:
                if work_days.code == 'WORK100':
                    payslip.total_hours = work_days.number_of_hours
            total_overtime = 0.0
            if total_timesheet_hours > payslip.total_hours:
                total_overtime = total_timesheet_hours - payslip.total_hours
                payslip.overtime_hours = total_overtime

    cheque_number = fields.Char("Cheque Number")
    active = fields.Boolean('Pay', default=True)
    pay_by_cheque = fields.Boolean('Pay By Cheque')
    employee_name = fields.Char(
        related='employee_id.name', string="Employee Name", store=True)
    active_employee = fields.Boolean(
        related='employee_id.active', string="Active Employee")
    total_timesheet_hours = fields.Float(
        compute='_get_total_hours', string='Total Timesheet Hours')
    total_hours = fields.Float(
        compute='_get_total_hours', string='Total Hours')
    overtime_hours = fields.Float(
        compute='_get_total_hours', string='Overtime Hours')
    pub_holiday_hours = fields.Float(
        compute='_get_total_public_holiday_hours',
        string='Public Holiday Hours')
    date = fields.Date(string="Payment Date")
    input_line_ids = fields.One2many(
        'hr.payslip.input', 'payslip_id', string='Payslip Inputs',
        readonly=True, states={'draft': [('readonly', False)]}, copy=True)

    def refund_sheet(self):
        """Refund sheet."""
        for payslip in self:
            if payslip.credit_note:
                raise ValidationError(_(
                    "You can not refund payslip which"
                    " is already refunded"))
            copied_payslip = payslip.copy(
                {'credit_note': True, 'name': _('Refund: ') + payslip.name})
            copied_payslip.compute_sheet()
            copied_payslip.action_payslip_done()
        formview_ref = self.env.ref('hr_payroll.view_hr_payslip_form', False)
        treeview_ref = self.env.ref('hr_payroll.view_hr_payslip_tree', False)
        return {
            'name': ("Refund Payslip"),
            'view_mode': 'tree, form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % copied_payslip.ids,
            'views': [(treeview_ref and treeview_ref.id or False, 'tree'),
                      (formview_ref and formview_ref.id or False, 'form')],
            'context': {}
        }

    @api.constrains('credit_note')
    def check_refund_payslip(self):
        """Check refund payslip."""
        for rec in self:
            payslip_ids = self.search([
                ('employee_id', '=', rec.employee_id.id),
                ('date_from', '=', rec.date_from),
                ('date_to', '=', rec.date_to),
                ('credit_note', '=', False)])
            if len(payslip_ids) > 1:
                for payslip in payslip_ids:
                    if payslip.credit_note is True:
                        continue
                    else:
                        raise ValidationError(
                            "You can not create multiple"
                            " payslip for same month")

    def check_time_zone(self, t_date):
        """Check time zone."""
        t_date = str(t_date)
        dt_value = t_date
        if t_date:
            timez = 'Singapore'
            if self._context and 'tz' in self._context:
                timez = self._context.get('tz')
            rec_date_from = datetime.strptime(str(t_date), DSDTF)
            src_tz = pytz.timezone('UTC')
            dst_tz = pytz.timezone(timez)
            src_dt = src_tz.localize(rec_date_from, is_dst=True)
            dt_value = src_dt.astimezone(dst_tz)
            dt_value = dt_value.strftime(DSDF)
        return dt_value

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        """Get worked day lines.

        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be
        applied for the given contract between date_from and date_to
        """
        def local_2_utc(str_date):
            if str_date:
                timez = 'Singapore'
                if self._context and 'tz' in self._context and \
                        self._context.get('tz') is not False:
                    timez = self._context.get('tz')
                local_tz = pytz.timezone(timez)
                datetime_without_tz = datetime.strptime(str(str_date), DSDTF)
                datetime_with_tz = local_tz.localize(
                    datetime_without_tz, is_dst=None)
                #  time
                datetime_in_utc = datetime_with_tz.astimezone(pytz.utc)
            return datetime_in_utc

        def was_on_leave(employee_id, datetime_day):
            holiday_obj = self.env['hr.leave']
            res1 = {'name': False, 'days': 0.0, 'half_work': False}

            #  day = datetime_day.strftime("%Y-%m-%d")
            day_fr = datetime_day.replace(hour=0, minute=0, second=0)
            day_fr = local_2_utc(day_fr.strftime(DSDTF))
            day_to = datetime_day.replace(hour=23, minute=59, second=59)
            day_to = local_2_utc(day_to.strftime(DSDTF))
            domain = [('state', '=', 'validate'),
                      ('employee_id', '=', employee_id),
                      ('request_date_from', '<=', day_to.strftime(DSDTF)),
                      ('request_date_to', '>=', day_fr.strftime(DSDTF))]
            holiday_ids = holiday_obj.search(domain)
            if holiday_ids:
                diff_day = holiday_obj._check_holiday_to_from_dates(
                    datetime_day, datetime_day, holiday_ids[0].employee_id.id)
                res = holiday_ids[0].holiday_status_id.name
                res1['name'] = res
                num_days = diff_day
                if holiday_ids[0].request_unit_half:
                    num_days = 0.5
                    res1['half_work'] = True
                res1['days'] = num_days
            return res1

        res = []
        for contract in contract_ids:
            if not contract.resource_calendar_id:
                #  fill only if the contract as a working schedule linked
                continue
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            leaves = {}
            day_from = datetime.strptime(str(date_from), "%Y-%m-%d")

            day_to = datetime.strptime(str(date_to), "%Y-%m-%d")

            nb_of_days = (day_to - day_from).days + 1
            d1 = datetime.strptime(str(date_from) + ' 00:00:00', DSDTF)
            d2 = datetime.strptime(str(date_from) + ' 23:59:59', DSDTF)
            resource_obj = self.env['resource.resource']
            resource_id = resource_obj.search([('user_id', '=',
                                                self.employee_id.user_id.id)],
                                              limit=1)
            for day in range(0, nb_of_days):
                calendar_id = contract.resource_calendar_id
                working_hours_on_day = calendar_id.get_work_hours_count(
                    d1 + timedelta(days=day), d2 + timedelta(days=day),
                    resource_id.id)
                if working_hours_on_day:
                    #  the employee had to work
                    leave_type = was_on_leave(
                        contract.employee_id.id, day_from +
                        timedelta(days=day))
                    if leave_type and leave_type['name']:
                        #  if he was on leave, fill the leaves dict
                        if leave_type['name'] in leaves:
                            leaves[leave_type['name']]['number_of_days'] +=\
                                leave_type['days']
                            leaves[leave_type['name']]['number_of_hours'] +=\
                                leave_type['days'] * working_hours_on_day
                        else:
                            leaves[leave_type['name']] = {
                                'name': leave_type['name'],
                                'sequence': 5,
                                'code': leave_type['name'],
                                'number_of_days': leave_type['days'],
                                'number_of_hours': leave_type['days'] *
                                working_hours_on_day,
                                'contract_id': contract.id,
                            }
                    else:
                        #  add the input vals to tmp (increment if existing)
                        from_date = datetime.fromtimestamp(time.mktime(
                            time.strptime(str(date_from), "%Y-%m-%d")))
                        curr_date = from_date + relativedelta(days=day)
                        curr_date = curr_date.date()
                        holiday_line_obj = self.env['hr.holiday.lines']
                        domain = [('holiday_id.state', '=', 'validated'),
                                  ('holiday_date', '=', str(curr_date))]
                        public_holiday_ids = holiday_line_obj.search(domain)
                        if public_holiday_ids:
                            continue
                        else:
                            attendances['number_of_days'] += 1.0
                            attendances['number_of_hours'] += (
                                working_hours_on_day)
            leaves = [value for key, value in leaves.items()]
            res += [attendances] + leaves
        return res

    @api.onchange('employee_id', 'date_from', 'date_to', 'contract_id')
    def onchange_employee(self):
        """Onchange employee.

        Based on employee set salary structure, working days, input line ids.
        """
        if self.employee_id and self.employee_id.id:
            employee_id = self.employee_id and self.employee_id.id
        else:
            employee_id = self._context.get('employee_id', False)

        if self.date_from:
            date_from = self.date_from
        else:
            date_from = self._context.get('date_from', False)

        if self.date_to:
            date_to = self.date_to
        else:
            date_to = self._context.get('date_to', False)

        if self.contract_id and self.contract_id.id:
            contract_id = self.contract_id and self.contract_id.id
        else:
            contract_id = self._context.get('contract_id', False)

        if (not employee_id) or (not date_from) or (not date_to):
            return {}

        empolyee_obj = self.env['hr.employee']
        period_end_date = date_to
        # delete old worked days lines
        old_worked_days_ids = []
        if self.id:
            old_worked_days_ids = [worked_days_rec.id for worked_days_rec in
                                   self.env['hr.payslip.worked_days'].search([
                                       ('payslip_id', '=', self.id)])]
        if old_worked_days_ids:
            self._cr.execute(""" delete from hr_payslip_worked_days \
                            where id in %s""", (tuple(old_worked_days_ids),))
        # delete old input lines
        old_input_ids = []
        if self.id:
            old_input_ids = [input_rec.id for input_rec in
                             self.env['hr.payslip.input'].search([
                                 ('payslip_id', '=', self.id)])]
        if old_input_ids:
            self._cr.execute(""" delete from hr_payslip_input where \
                                id in %s""", (tuple(old_input_ids),))
        res = {'value': {
            'line_ids': [],
            'input_line_ids': [],
            'worked_days_line_ids': [],
            'name': '',
            'contract_id': False,
            'struct_id': False}}
        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(
            str(date_from),
            "%Y-%m-%d")))
        employee_brw = empolyee_obj.browse(employee_id)
        res['value'].update({
            'name': _('Salary Slip of %s for %s') % (
                employee_brw.name, tools.ustr(ttyme.strftime('%B-%Y'))
            ),
            'company_id': employee_brw.company_id and
            employee_brw.company_id.id or False
        })
        if not self._context.get('contract', False):
            # fill with the first contract of the employee
            contract_ids = self.get_contract(employee_brw, date_from, date_to)
        else:
            if contract_id:
                # set the list of contract for which the input have
                # to be filled
                contract_ids = [contract_id]
            else:
                # if we don't give the contract, then the input to fill should
                # be for all current contracts of the employee
                contract_ids = self.get_contract(employee_brw, date_from,
                                                 date_to)
        if not contract_ids:
            return res
        contract_record = self.env['hr.contract'].browse(contract_ids[0])
        res['value'].update(
            {'contract_id': contract_record.id if contract_record else False})
        struct_record = contract_record.struct_id \
            if contract_record.struct_id else False
        if not struct_record:
            return res
        res['value'].update({
            'struct_id': struct_record.id,
        })
        # computation of the salary input
        brw_contract_ids = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(brw_contract_ids,
                                                         date_from.strftime(
                                                             DSDF),
                                                         date_to.strftime(DSDF
                                                                          ))
        contract_records = self.env['hr.contract'].browse(contract_ids)
        input_line_ids = self.get_inputs(contract_records, date_from, date_to)
        res['value'].update({
            'worked_days_line_ids': worked_days_line_ids,
            'input_line_ids': input_line_ids,
        })
        if not employee_id:
            return res
        active_employee = empolyee_obj.browse(employee_id).active
        res['value'].update({'active_employee': active_employee})
        res['value'].update({'employee_id': employee_id,
                             'date_from': date_from, 'date_to': date_to})
        if date_from and date_to:
            current_date_from = date_from
            current_date_to = date_to
            date_from_cur = date_from
            previous_month_obj = parser.parse(date_from_cur.strftime(DSDF)) - \
                relativedelta(months=1)
            total_days = calendar.monthrange(previous_month_obj.year,
                                             previous_month_obj.month)[1]
            first_day_of_previous_month = datetime.strptime("1-" + str(
                previous_month_obj.month) + "-" +
                str(previous_month_obj.year), '%d-%m-%Y')
            last_day_of_previous_month = datetime.strptime(
                str(total_days) + "-" + str(previous_month_obj.month) +
                "-" + str(previous_month_obj.year), '%d-%m-%Y')
            date_from = datetime.strftime(first_day_of_previous_month, DSDF)
            date_to = datetime.strftime(last_day_of_previous_month, DSDF)
            dates = list(rrule.rrule(rrule.DAILY,
                                     dtstart=parser.parse(date_from),
                                     until=parser.parse(date_to)))
            sunday = saturday = weekdays = 0
            for day in dates:
                if day.weekday() == 5:
                    saturday += 1
                elif day.weekday() == 6:
                    sunday += 1
                else:
                    weekdays += 1
            new = {'code': 'TTLPREVDAYINMTH',
                   'name': 'Total number of days for \
                    previous month', 'number_of_days': len(dates),
                   'sequence': 2, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code': 'TTLPREVSUNINMONTH', 'name': 'Total sundays in \
                    previous month', 'number_of_days': sunday,
                   'sequence': 3, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code': 'TTLPREVSATINMONTH', 'name': 'Total saturdays in \
                    previous month', 'number_of_days': saturday,
                   'sequence': 4, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code': 'TTLPREVWKDAYINMTH', 'name': 'Total weekdays in \
                    previous month', 'number_of_days': weekdays,
                   'sequence': 5, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)

            # added no holidays in current month.
            f = period_end_date
            count = 0
            currentz_yearz = datetime.strptime(str(f), DSDF).year
            currentz_mnthz = datetime.strptime(str(f), DSDF).month

            holiday_brw = self.env['hr.holiday.public'].search([
                ('state', '=',
                 'validated')])
            if holiday_brw and holiday_brw.ids:
                for line in holiday_brw:
                    if line.holiday_line_ids and line.holiday_line_ids.ids:
                        for holiday in line.holiday_line_ids:
                            holidyz_mnth = datetime.strptime(
                                str(holiday.holiday_date), DSDF
                            ).month
                            holiday_year = datetime.strptime(
                                str(holiday.holiday_date), DSDF
                            ).year
                            if currentz_yearz == holiday_year and \
                                    holidyz_mnth == currentz_mnthz:
                                count = count + 1

            new = {'code': 'PUBLICHOLIDAYS', 'name': 'Total Public Holidays in\
                    current month', 'number_of_days': count,
                   'sequence': 6, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)

            # end of holiday calculation
            this_month_obj = parser.parse(date_from_cur.strftime(DSDF)
                                          ) + relativedelta(months=1, days=-1)
            dates = list(rrule.rrule(rrule.DAILY,
                                     dtstart=parser.parse(str(current_date_from
                                                              )),
                                     until=parser.parse(str(current_date_to))))
            total_days_cur_month = calendar.monthrange(this_month_obj.year,
                                                       this_month_obj.month)[1]
            first_day_of_current_month = datetime.strptime(
                "1-" + str(this_month_obj.month) + "-" + str(
                    this_month_obj.year), '%d-%m-%Y')
            last_day_of_current_month = datetime.strptime(
                str(total_days_cur_month) +
                "-" + str(this_month_obj.month) +
                "-" + str(this_month_obj.year),
                '%d-%m-%Y')
            th_current_date_from = datetime.strftime(
                first_day_of_current_month, DSDF)
            th_current_date_to = datetime.strftime(last_day_of_current_month,
                                                   DSDF)
            cur_dates = list(rrule.rrule(
                rrule.DAILY,
                dtstart=parser.parse(th_current_date_from),
                until=parser.parse(th_current_date_to)))
            sunday = saturday = weekdays = 0
            cur_sunday = cur_saturday = cur_weekdays = 0
            for day in dates:
                if day.weekday() == 5:
                    saturday += 1
                elif day.weekday() == 6:
                    sunday += 1
                else:
                    weekdays += 1
            for day in cur_dates:
                if day.weekday() == 5:
                    cur_saturday += 1
                elif day.weekday() == 6:
                    cur_sunday += 1
                else:
                    cur_weekdays += 1
            new = {'code': 'TTLDAYINMTH',
                   'name': 'Total days for current month',
                   'number_of_days': len(cur_dates), 'sequence': 7,
                   'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code': 'TTLCURRDAYINMTH',
                   'name': 'Total number of days for current month',
                   'number_of_days': len(dates),
                   'sequence': 2, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code': 'TTLCURRSUNINMONTH',
                   'name': 'Total sundays in current month',
                   'number_of_days': sunday, 'sequence': 3,
                   'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code': 'TTLCURRSATINMONTH',
                   'name': 'Total saturdays in current month',
                   'number_of_days': saturday,
                   'sequence': 4, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code': 'TTLCURRWKDAYINMTH',
                   'name': 'Total weekdays in current month',
                   'number_of_days': weekdays,
                   'sequence': 5, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            new = {'code': 'TTLCURRWKDAYINHMTH',
                   'name': 'Total weekdays in whole current month',
                   'number_of_days': cur_weekdays,
                   'sequence': 8, 'contract_id': contract_record.id}
            res.get('value').get('worked_days_line_ids').append(new)
            cur_month_weekdays = 0

            if contract_record:
                contract_start_date = contract_record.date_start
                contract_end_date = contract_record.date_end
                if contract_start_date and contract_end_date:

                    if current_date_from <= contract_start_date and \
                            contract_end_date <= current_date_to:
                        current_month_days = list(rrule.rrule(
                            rrule.DAILY, dtstart=parser.parse(str(
                                contract_start_date)),
                            until=parser.parse(str(contract_end_date))))
                        for day in current_month_days:
                            if day.weekday() not in [5, 6]:
                                cur_month_weekdays += 1

                    elif current_date_from <= contract_start_date and \
                            current_date_to <= contract_end_date:
                        current_month_days = list(rrule.rrule(
                            rrule.DAILY, dtstart=parser.parse(str(
                                contract_start_date)),
                            until=parser.parse(str(current_date_to))))
                        for day in current_month_days:
                            if day.weekday() not in [5, 6]:
                                cur_month_weekdays += 1

                    elif contract_start_date <= current_date_from and \
                            contract_end_date <= current_date_to:
                        current_month_days = list(rrule.rrule(
                            rrule.DAILY, dtstart=parser.parse(str(
                                current_date_from)),
                            until=parser.parse(str(contract_end_date))))
                        for day in current_month_days:
                            if day.weekday() not in [5, 6]:
                                cur_month_weekdays += 1

            if cur_month_weekdays:
                new = {'code': 'TTLCURCONTDAY',
                       'name': 'Total current contract \
                        days in current month',
                       'number_of_days': cur_month_weekdays,
                       'sequence': 6, 'contract_id': contract_record.id}
                res.get('value').get('worked_days_line_ids').append(new)
            else:
                new = {'code': 'TTLCURCONTDAY', 'name': 'Total current\
                contract days in current month', 'number_of_days': weekdays,
                       'sequence': 6, 'contract_id': contract_record.id}
                res.get('value').get('worked_days_line_ids').append(new)
        if employee_id:
            emp_obj = self.env["hr.employee"]
            emp_rec = emp_obj.browse(employee_id)
            holiday_status_obj = self.env["hr.leave.type"]
            if emp_rec.leave_config_id:
                for h_staus in emp_rec.leave_config_id.\
                        holiday_group_config_line_ids:
                    flag = False
                    for payslip_data in \
                            res["value"].get("worked_days_line_ids"):
                        if payslip_data.get("code") == \
                                h_staus.leave_type_id.name:
                            if "name" in payslip_data:
                                payslip_data.update({
                                    "name": h_staus.leave_type_id.name2
                                })
                            flag = True
                    if not flag:
                        new = {'code': h_staus.leave_type_id.name,
                               'name': h_staus.leave_type_id.name2,
                               'number_of_days': 0.0, 'sequence': 0,
                               'contract_id': contract_record.id}
                        res.get('value').get(
                            'worked_days_line_ids').append(new)
            else:
                holidays_status_ids = holiday_status_obj.search([])
                for holiday_status in holidays_status_ids:
                    flag = False
                    for payslip_data in res["value"].get(
                            "worked_days_line_ids"):
                        if payslip_data.get("code") == holiday_status.name:
                            flag = True
                    if not flag:
                        new = {'code': holiday_status.name,
                               'name': holiday_status.name2,
                               'number_of_days': 0.0, 'sequence': 0,
                               'contract_id': contract_record.id}
                        res.get('value').get(
                            'worked_days_line_ids').append(new)
        if not self._context.get('from_wiz'):
            worked_days_lines = self.worked_days_line_ids.browse([])
            input_lines = self.input_line_ids.browse([])
            for line in res.get('value', []).get('worked_days_line_ids', []):
                worked_days_lines += worked_days_lines.new(line)
            for line in res.get('value', []).get('input_line_ids', []):
                input_lines += input_lines.new(line)
            res.get('value', [])['worked_days_line_ids'] = worked_days_lines
            res.get('value', [])['input_line_ids'] = input_lines
        return res

    def compute_sheet(self):
        """Compute sheet."""
        result = super(HrPayslip, self).compute_sheet()
        lines = []
        for payslip in self:
            for line in payslip.line_ids:
                if line.amount == 0:
                    lines.append(line.id)
        if lines:
            line_rec = self.env['hr.payslip.line'].browse(lines)
            line_rec.unlink()
        return result


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    identification_no = fields.Selection([('1', 'NRIC'), ('2', 'FIN'),
                                          ('3', 'Immigration File Ref No.'),
                                          ('4', 'Work Permit No'),
                                          ('5',
                                           'Malaysian I/C (for non-resident \
                                           director and seaman only)'),
                                          ('6', 'Passport No. (for \
                                          non-resident director and seaman \
                                          only)')],
                                         string='2. ID Type of Employee')
    address_type = fields.Selection([('L', 'Local residential address'),
                                     ('F', 'Foreign address'),
                                     ('C', 'Local C/O address'),
                                     ('N', 'Not Available')],
                                    string='Address Type')
    empcountry_id = fields.Many2one('employee.country',
                                    '6(k). Country Code of address')
    empnationality_id = fields.Many2one('employee.nationality',
                                        '7. Nationality Code')
    cessation_provisions = fields.Selection([('Y',
                                              'Cessation Provisions \
                                              applicable'),
                                             ('N',
                                              'Cessation Provisions not \
                                              applicable')],
                                            string='28. Cessation Provisions')
    employee_type = fields.Selection([('full_employeement',
                                       'Full Employer & Graduated Employee \
                                       (F/G)'),
                                      ('graduated_employee',
                                       'Graduated Employer & Employee (G/G)')],
                                     string='Employee Type',
                                     default='full_employeement')
    payslip_count = fields.Integer(compute='_compute_payslip_count',
                                   string='Payslips',
                                   groups="base.group_user")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Search.

        Override Search method for put filter on current working status.
        """
        context = self.env.context
        if context and context.get('batch_start_date') and context.get(
                'batch_end_date'):
            active_contract_employee_list = []
            contract_ids = self.env['hr.contract'].search(
                ['|', ('date_end', '>=', context.get('batch_start_date')),
                 ('date_end', '=', False),
                 ('date_start', '<=',
                  context.get('batch_end_date'))])
            for contract in contract_ids:
                active_contract_employee_list.append(contract.employee_id.id)
            args.append(('id', 'in', active_contract_employee_list))
        return super(HrEmployee, self).search(args, offset, limit, order,
                                              count=count)


class EmployeeCountry(models.Model):
    _name = 'employee.country'
    _description = "Employee Country"

    name = fields.Char('Country', required=True)
    code = fields.Integer('Code', required=True)


class EmployeeNationality(models.Model):
    _name = 'employee.nationality'
    _description = "Employee Nationality"

    name = fields.Char('Nationality', required=True)
    code = fields.Integer('Code', required=True)


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    _description = 'Payslip Batches'

    @api.constrains('date_start', 'date_end')
    def _check_payslip_date(self):
        if self.date_start > self.date_end:
            raise ValidationError("Date From' must be before 'Date To")

    def open_payslip_employee(self):
        """Open payslip employee."""
        context = self.env.context
        if context is None:
            context = {}
        context = dict(context)
        context.update({'default_date_start': self.date_start,
                        'default_date_end': self.date_end})
        return {'name': ('Payslips by Employees'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.payslip.employees',
                'type': 'ir.actions.act_window',
                'target': 'new'}


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_ids = fields.Many2many('res.users', 'ppd_res_user_payroll_rel',
                                'usr_id', 'user_id', 'User Name')


class ResCompany(models.Model):
    _inherit = 'res.company'

    company_code = fields.Char('Company Code')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    level_no = fields.Char('Level No')
    house_no = fields.Char('House No')
    unit_no = fields.Char('Unit No')


class HrPayslipInput(models.Model):
    _inherit = "hr.payslip.input"

    @api.onchange('code')
    def onchange_code(self):
        if self.code:
            self.contract_id = self.payslip_id.contract_id.id
