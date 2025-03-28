odoo.define('h202_gst_reports_transactions.BalanceSheetReport', function (require) {
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
    var BalanceSheetReport = AbstractAction.extend({
        template: 'TempBalanceSheetReport',
        events: {
            'click #filter_apply_button': 'update_with_filter',
            'click #open_account_move': 'view_account_move',
            'click #pdf': 'print_pdf',
            'click #xlsx': 'print_xlsx',
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
                    model: 'balance.sheet.report',
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
        view_account_move: function (event) {
            event.preventDefault();
            var self = this;
            var account_id = $(event.currentTarget).data('account-id')
            self._rpc({
                model: 'balance.sheet.report',
                method: 'get_account_move_action',
                args: [[self.wizard_id],account_id],
            }).then(function (action) {
                action = _.extend(action, {
                    'view_mode': 'list,form',
                    'views':  [[false, 'list'], [false, 'form']],
                });
                return self.do_action(action);
            })
        },
        plot_data: function (initial_render = true) {
            var self = this;
            self.loader_disable_ui();
            var node = self.$('.py-data-container-orig');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'balance.sheet.report',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterBalanceSheetReport', {get_info: datas}));
                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    })
                    self.$el.find('.analytic-multiple').select2({
                        placeholder: 'Extra Options...',
                    })
                }
                self.$('.py-data-container-orig').html(QWeb.render('TempBalanceSheetReportMain', {
                    get_info: datas,
                }));
                self.loader_enable_ui();
            });
        },
        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {hide_line: false, date_from_cmp: false, date_to_cmp: false,
                number_of_comparison: 0, comparison_number_of_month: 0, comparison_number_of_year: 0};

            if ($("#date_from").val()) {
                output['start_date'] = self.$el.find('#date_from').val();
            }

            if ($("#date_to").val()) {
                output['end_date'] = self.$el.find('#date_to').val();;
            }

            if ($("#date_from_cmp").val()) {
                output['date_from_cmp'] = self.$el.find('#date_from_cmp').val();
            }

            if ($("#date_to_cmp").val()) {
                output['date_to_cmp'] = self.$el.find('#date_to_cmp').val();;
            }

            if ($("#number_of_comparison").val()) {
                output['number_of_comparison'] = $("#number_of_comparison").val()
            }

            if ($("#comparison_number_of_month").val()) {
                output['comparison_number_of_month'] = $("#comparison_number_of_month").val()
            }

            if ($("#comparison_number_of_year").val()) {
                output['comparison_number_of_year'] = $("#comparison_number_of_year").val()
            }

            var analytic_account_ids = [];
            var unassigned_analytic = false
            var analytic_list = $(".analytic-multiple").select2('data')
            for (var i = 0; i < analytic_list.length; i++) {
                if (analytic_list[i].id == 0) {
                    unassigned_analytic = true
                }
                else {
                    analytic_account_ids.push(parseInt(analytic_list[i].id))
                }
            }
            output.unassigned_analytic = unassigned_analytic
            output.analytic_account_ids = analytic_account_ids

            var options_list = $(".extra-multiple").select2('data')
            for (var i = 0; i < options_list.length; i++) {
                if (options_list[i].id === 'hide_line') {
                    output.hide_line = true;
                }
            }

            self._rpc({
                model: 'balance.sheet.report',
                method: 'write',
                args: [self.wizard_id, output],
            }).then(function (res) {
                self.plot_data(self.initial_render);
            });
        },
        print_pdf: function (e) {
            e.preventDefault();
            var self = this;
            self._rpc({
                model: 'balance.sheet.report',
                method: 'check_report',
                args: [[self.wizard_id]],
            }).then(function (action) {
                action['context'] = {
                    'active_model': 'balance.sheet.report',
                    'active_id': self.wizard_id,
                }
                return self.do_action(action);
            });
        },
        print_xlsx: function () {
            var self = this;
            self._rpc({
                model: 'balance.sheet.report',
                method: 'action_xlsx',
                args: [[self.wizard_id]],
            }).then(function (action) {
                action.context.active_ids = [self.wizard_id];
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

    core.action_registry.add('balance.sheet.report', BalanceSheetReport);

    return {
        BalanceSheetReport: BalanceSheetReport,
    };
});
