odoo.define('s2u_online_appoinment.main', function (require) {
    'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var _t = core._t;

    publicWidget.registry.OnlineAppointment = publicWidget.Widget.extend({
        selector: '#das_online_appointment',
        init: function () {
            this._super.apply(this, arguments);

            this.days_with_free_slots = {};
            this.focus_year = 0;
            this.focus_month = 0;
        },
        start: function () {
            var self = this;

            $('.datepicker').datepicker({
                dateFormat: 'dd/mm/yy',
                startDate: '-3d',
                beforeShowDay: function(date) {
                    var d = self._format_date(date);
                    var key = date.getFullYear().toString() + ','+ (date.getMonth() + 1).toString();
                    if (self.days_with_free_slots[key] && self.days_with_free_slots[key][d]) {
                        return [true, 'color_green', ''];
                    } else {
                        return [false, '', ''];
                    }
                },
                onChangeMonthYear: function(year, month, datepicker) {
                    self._update_days_with_free_slots(year, month);
                },
            });
            $('#timeslot_id').change(function () {
                const d = new Date();

                var month = d.getMonth() + 1;
                var year = d.getFullYear();

                self._rpc({
                route: '/online-appointment/month-bookable',
                params: {
                    'timeslot_id': $("#timeslot_id").val(),
                    'appointment_year': year,
                    'appointment_month': month,
                    'form_criteria': $("#form_criteria").val(),
                },
            }).then(function(result) {
                self.focus_year = result.focus_year;
                self.focus_month = result.focus_month;
                self.days_with_free_slots[self._get_yearmonth_key.bind(self)()] = result.days_with_free_slots;
                $(".datepicker" ).datepicker("refresh");
            });
            })
            // $('.datepicker').datepicker({
            //     format: 'dd-mm-yy',
            //     icons: {
            //         time: "fa fa-clock-o",
            //         date: "fa fa-calendar",
            //         up: "fa fa-chevron-up",
            //         down: "fa fa-chevron-down",
            //         previous: 'fa fa-chevron-left',
            //         next: 'fa fa-chevron-right',
            //         today: 'fa fa-screenshot',
            //         clear: 'fa fa-trash',
            //         close: 'fa fa-remove'
            //     }
            // });
        },

        _format_date: function (date) {
            var self = this;

            var d = new Date(date),
                month = '' + (d.getMonth() + 1),
                day = '' + d.getDate(),
                year = d.getFullYear();

            if (month.length < 2)
                month = '0' + month;
            if (day.length < 2)
                day = '0' + day;

            return [year, month, day].join('-');
        },

        _update_days_with_free_slots: function (year, month) {
            var self = this;

            this._rpc({
                route: '/online-appointment/month-bookable',
                params: {
                    'timeslot_id': $("#timeslot_id").val(),
                    'appointment_year': year,
                    'appointment_month': month,
                    'form_criteria': $("#form_criteria").val(),
                },
            }).then(function(result) {
                self.focus_year = result.focus_year;
                self.focus_month = result.focus_month;
                self.days_with_free_slots[self._get_yearmonth_key.bind(self)()] = result.days_with_free_slots;
                $(".datepicker" ).datepicker("refresh");
            });
        },

        _get_yearmonth_key: function() {
            var key = this.focus_year.toString() + ',' + this.focus_month.toString();
            return key
        },

    }),

    publicWidget.registry.OnlineAppointmentPortal = publicWidget.Widget.extend({
        selector: '#online_appointment_interaction',
        start: function () {
            var self = this;
            var button_cancel = $('#cancel_appointment_button');
            var button_confirm = $('#confirm_appointment_button');

            button_cancel.click(function() {
                var dialog = $('#cancel_appointment_dialog').modal('show');
            });

            button_confirm.click(function() {
                var dialog = $('#confirm_appointment_dialog').modal('show');
            });
        }
    })
});
