odoo.define('wk39717700c_modifier_print.AgeingSummaryReport', function (require) {
    'use strict';
    var ActionManager = require('web.ActionManager');
    var AbstractAction = require('web.AbstractAction');
    var Dialog = require('web.Dialog');
    var FavoriteMenu = require('web.FavoriteMenu');
    var web_client = require('web.web_client');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var field_utils = require('web.field_utils');
    var rpc = require('web.rpc');
    var time = require('web.time');
    var session = require('web.session');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;
    var QWeb = core.qweb;
    var _t = core._t;
    var exports = {};

    var AgeingSummaryReport = AbstractAction.extend({
        template: 'TempAgeingSummaryReport',
        events: {
            'click #filter_apply_button': 'update_with_filter',
            'click #pdf': 'print_pdf',
            'click .term-parent': 'show_detail',
        },
        init: function (view, code) {
            this._super(view, code);
            this.wizard_id = code.context.wizard_id | null;
            this.session = session;
        },
        start: function () {
            var self = this;
            self.initial_render = true;
            if (!self.wizard_id) {
                self._rpc({
                    model: 'ageing.summary.report',
                    method: 'create',
                    args: [{res_model: this.res_model}]
                }).then(function (record) {
                    self.wizard_id = record;
                    self.plot_data(self.initial_render);
                })
            } else {
                self.plot_data(self.initial_render);
            }
        },
        plot_data: function (initial_render = true) {
            var self = this;
            self.loader_disable_ui();
            var node = self.$('.py-data-container-orig');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ageing.summary.report',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterAgeingSummaryReport', {get_info: datas}));
                    self.$el.find('.customer-multiple').select2({
                        placeholder: 'Select Customer...',
                    });
                    self.$el.find('.user-multiple').select2({
                        placeholder: 'Select Salesman...',
                    });
                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    })
                    if (datas['hide_line']) {
                        $(".extra-multiple").select2('data', [{id: 'hide_line', text: 'Hide line not have value'}])
                    }
                    self.$el.find('.term-multiple').select2({
                        placeholder: 'Select Term...',
                    })
                }
                self.$('.py-data-container-orig').html(QWeb.render('TempAgeingSummaryReportMain', {
                    get_info: datas,
                }));
                self.loader_enable_ui();
            });
        },
        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {hide_line: false, term_ids: false};

            if ($("#closed_date").val()) {
                output['closed_date'] = self.$el.find('#closed_date').val();
            }
            var customer_ids = [];
            var customer_list = $(".customer-multiple").select2('data')
            for (var i = 0; i < customer_list.length; i++) {
                customer_ids.push(parseInt(customer_list[i].id))
            }
            output.customer_ids = customer_ids

            var user_list = $(".user-multiple").select2('data')
            if (user_list.length > 0) {
                var user_ids = [];
                for (var i = 0; i < user_list.length; i++) {
                    user_ids.push(parseInt(user_list[i].id))
                }
                output.user_ids = user_ids
            }

            var options_list = $(".extra-multiple").select2('data')
            for (var i = 0; i < options_list.length; i++) {
                if (options_list[i].id === 'hide_line') {
                    output.hide_line = true;
                }
            }

            var term_list = $(".term-multiple").select2('data')
            if (term_list.length > 0) {
                var term_ids = [];
                for (var i = 0; i < term_list.length; i++) {
                    term_ids.push(parseInt(term_list[i].id))
                }
                output.term_ids = term_ids
            }

            self._rpc({
                model: 'ageing.summary.report',
                method: 'write',
                args: [self.wizard_id, output],
            }).then(function (res) {
                self.plot_data(self.initial_render);
            });
        },
        show_detail: function (e) {
            var data_term = $(e.currentTarget).data('term');
            var class_term = '.' + data_term
            this.$(class_term).hasClass('o_hidden') ? this.$(class_term).removeClass('o_hidden') : this.$(class_term).addClass('o_hidden');
        },
        print_pdf: function (e) {
            e.preventDefault();
            var self = this;
            self._rpc({
                model: 'ageing.summary.report',
                method: 'generate_pdf_report',
                args: [[self.wizard_id]],
            }).then(function (action) {
                action['context'] = {
                    'active_model': 'ageing.summary.report',
                    'active_id': self.wizard_id,
                }
                return self.do_action(action);
            });
        },
        loader_disable_ui: function () {
            $('.py-main-container').addClass('ui-disabled');
            $('.py-main-container').css({'opacity': '0.4', 'cursor': 'wait'});
            $('#loader').css({'visibility': 'visible', 'opacity': '1'});
        },
        loader_enable_ui: function () {
            $('.py-main-container').removeClass('ui-disabled');
            $('#loader').css({'visibility': 'hidden'});
            $('.py-main-container').css({'opacity': '1', 'cursor': 'auto'});
        },
    });

    core.action_registry.add('ageing.summary', AgeingSummaryReport);

    return {
        AgeingSummaryReport: AgeingSummaryReport,
    };
});
