odoo.define('profit_and_loss_by_projects.DynamicPrMain', function (require) {
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
    var DynamicPrMain = AbstractAction.extend({
        template: 'DynamicPrMain',
        events: {
            'click #filter_apply_button': 'update_with_filter',
            'click #pdf': 'print_pdf',
            'click #xlsx': 'print_xlsx',
            'click .view-source': 'view_gl',
        },
        init: function (view, code) {
            this._super(view, code);
            this.wizard_id = code.context.wizard_id | null;
            this.account_report_id = code.context.account_report_id | null;
            this.session = session;
        },
        start: function () {
            var self = this;
            self.initial_render = true;
            if (!self.wizard_id) {
                self._rpc({
                    model: 'ins.financial.report',
                    method: 'create',
                    context: {report_name: this.account_report_id},
                    args: [{
                        res_model: this.res_model,
                    }]
                }).then(function (record) {
                    self.wizard_id = record;
                    self.plot_data(self.initial_render);
                })
            } else {
                self.plot_data(self.initial_render);
            }
        },
        print_pdf: function (e) {
            e.preventDefault();
            var self = this;
            self._rpc({
                model: 'ins.financial.report',
                method: 'get_report_values_pr',
                args: [[self.wizard_id]],
            }).then(function (data) {
                var action = {
                    'type': 'ir.actions.report',
                    'report_type': 'qweb-pdf',
                    'report_name': 'profit_and_loss_by_projects.ins_report_financial_pr',
                    'report_file': 'profit_and_loss_by_projects.ins_report_financial_pr',
                    'data': {'data': data},
                    'context': {
                        'active_model': 'ins.financial.report',
                        'landscape': 1,
                        'from_js': true
                    },
                    'display_name': 'Finance Report',
                };
                return self.do_action(action);
            });
        },
        print_xlsx: function () {
            var self = this;
            self._rpc({
                model: 'ins.financial.report',
                method: 'action_xlsx_pr',
                args: [[self.wizard_id]],
            }).then(function (action) {
                action.context.active_ids = [self.wizard_id];
                return self.do_action(action);
            });
        },
        print_xlsx_new : function() {
            var self = this;
            self._rpc({
                model: 'ins.financial.report',
                method: 'action_xlsx_custom',
                args: [[self.wizard_id]],
            }).then(function (action) {
                action.context.active_ids = [self.wizard_id];
                return self.do_action(action);
            });
        },
        formatWithSign: function (amount, formatOptions, sign) {
            var currency_id = formatOptions.currency_id;
            currency_id = session.get_currency(currency_id);
            var without_sign = field_utils.format.monetary(Math.abs(amount), {}, formatOptions);
            if (!amount) {
                return false
            }
            ;
            if (currency_id.position === "after") {
                return sign + '&nbsp;' + without_sign + '&nbsp;' + currency_id.symbol;
            } else {
                return currency_id.symbol + '&nbsp;' + sign + '&nbsp;' + without_sign;
            }
            return without_sign;
        },

        formatWithSignTotal: function (amount, formatOptions, sign) {
            var currency_id = formatOptions.currency_id;
            currency_id = session.get_currency(currency_id);
            var without_sign = field_utils.format.monetary(Math.abs(amount), {}, formatOptions);
            if (!amount) {
                return '-'
            }
            ;
            if (currency_id.position === "after") {
                return sign + '&nbsp;' + without_sign + '&nbsp;' + currency_id.symbol;
            } else {
                return currency_id.symbol + '&nbsp;' + sign + '&nbsp;' + without_sign;
            }
            return without_sign;
        },
        plot_data: function (initial_render = true) {
            var self = this;
            var node = self.$('.py-data-container');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.financial.report',
                method: 'get_report_values_pr',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas.form;
                self.account_data = datas.report_lines;
                self.analytics_list = datas.analytics_list;
                self.analytics_len = datas.analytics_len;
                var formatOptions = {
                    currency_id: datas.currency,
                    noSymbol: true,
                };
                self.initial_balance = self.formatWithSign(datas.initial_balance, formatOptions, datas.initial_balance < 0 ? '-' : '');
                self.current_balance = self.formatWithSign(datas.current_balance, formatOptions, datas.current_balance < 0 ? '-' : '');
                self.ending_balance = self.formatWithSign(datas.ending_balance, formatOptions, datas.ending_balance < 0 ? '-' : '');
                _.each(self.account_data, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.balance_cmp = self.formatWithSign(k.balance_cmp, formatOptions, k.balance < 0 ? '-' : '');

                    var project_line = k.project_line
                    var total_project = 0
                    _.each(project_line, function (key, value) {
                        total_project += key[0]
                        key[0] = self.formatWithSign(key[0], formatOptions, key[0] < 0 ? '-' : '');
                    });

                    k.total_project = self.formatWithSign(total_project, formatOptions, total_project < 0 ? '-' : '');
                });
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterSectionPr', {
                        filter_data: self.filter_data,
                    }));
                    self.$el.find('#date_from').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('#date_to').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('#date_from_cmp').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('#date_to_cmp').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('.date_filter-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Date...',
                    });
                    self.$el.find('.journal-multiple').select2({
                        placeholder: 'Select Journal...',
                    });
                    self.$el.find('.analytic-tag-multiple').select2({
                        placeholder: 'Analytic Tags...',
                    });
                    self.$el.find('.analytic-multiple').select2({
                        placeholder: 'Select Analytic...',
                    });
                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    })
                        .val('debit_credit').trigger('change')
                    ;
                }
                self.$('.py-data-container').html(QWeb.render('DataSectionPr', {
                    account_data: self.account_data,
                    filter_data: self.filter_data,
                    analytics_list: self.analytics_list,
                    analytics_len: self.analytics_len,
                }));
                if (parseFloat(datas.initial_balance) > 0 || parseFloat(datas.current_balance) > 0 || parseFloat(datas.ending_balance) > 0) {
                    $(".py-data-container").append(QWeb.render('SummarySectionPr', {
                        initial_balance: self.initial_balance,
                        current_balance: self.current_balance,
                        ending_balance: self.ending_balance
                    }));
                }
            });
        },
        view_gl: function (event) {
            event.preventDefault();
            var self = this;
            if (self.filter_data.date_from == false || self.filter_data.date_to == false) {
                alert("'Start Date' and 'End Date' are mandatory!");
                return true;
            }
            var domains = {
                account_ids: [$(event.currentTarget).data('account-id')],
                initial_balance: (self.filter_data.rtype == 'CASH' || self.filter_data.rtype == 'PANDL') ? false : true
            }
            var context = {};
            if ($("#date_from").val()) {
                var dateObject = $("#date_from").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                domains.date_from = dateString;
            }
            if ($("#date_to").val()) {
                var dateObject = $("#date_to").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                domains.date_to = dateString;
            }
            if (!domains.date_from && !domains.date_to && !domains.date_range) {
                domains.date_from = self.filter_data.date_from;
                domains.date_to = self.filter_data.date_to;
            }
            var journal_ids = [];
            var journal_list = $(".journal-multiple").select2('data')
            for (var i = 0; i < journal_list.length; i++) {
                journal_ids.push(parseInt(journal_list[i].id))
            }
            domains.journal_ids = journal_ids
            var analytic_ids = [];
            var analytic_list = $(".analytic-multiple").select2('data')
            for (var i = 0; i < analytic_list.length; i++) {
                analytic_ids.push(parseInt(analytic_list[i].id))
            }
            domains.analytic_ids = analytic_ids
            var analytic_tag_ids = [];
            var analytic_tag_list = $(".analytic-tag-multiple").select2('data')
            for (var i = 0; i < analytic_tag_list.length; i++) {
                analytic_tag_ids.push(parseInt(analytic_tag_list[i].id))
            }
            domains.analytic_tag_ids = analytic_tag_ids
            var fr_wizard_id = 0;
            self._rpc({
                model: 'ins.general.ledger',
                method: 'create',
                args: [{}]
            }).then(function (record) {
                fr_wizard_id = record;
                self._rpc({
                    model: 'ins.general.ledger',
                    method: 'write',
                    args: [fr_wizard_id, domains]
                }).then(function () {
                    var action = {
                        type: 'ir.actions.client',
                        name: 'GL View',
                        tag: 'dynamic.gl',
                        nodestroy: true,
                        target: 'new',
                        context: {
                            wizard_id: fr_wizard_id,
                            active_id: self.wizard_id,
                            active_model: 'ins.financial.report'
                        }
                    }
                    return self.do_action(action);
                })
            })
        },
        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {date_range: false, enable_filter: false, debit_credit: false};
            if ($(".date_filter-multiple").select2('data').length === 1) {
                output.date_range = $(".date_filter-multiple").select2('data')[0].id
            }
            if ($("#date_from").val()) {
                var dateObject = $("#date_from").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_from = dateString;
                output.date_to = false;
            }
            if ($("#date_to").val()) {
                var dateObject = $("#date_to").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_to = dateString;
                output.date_from = false;
            }
            if ($("#date_from").val() && $("#date_to").val()) {
                var dateObject = $("#date_from").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_from = dateString;
                var dateObject = $("#date_to").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_to = dateString;
            }
            if ($("#date_from_cmp").val()) {
                var dateObject = $("#date_from_cmp").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_from_cmp = dateString;
                output.enable_filter = true;
            }
            if ($("#date_to_cmp").val()) {
                var dateObject = $("#date_to_cmp").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.date_to_cmp = dateString;
                output.enable_filter = true;
            }
            var journal_ids = [];
            var journal_list = $(".journal-multiple").select2('data')
            for (var i = 0; i < journal_list.length; i++) {
                journal_ids.push(parseInt(journal_list[i].id))
            }
            output.journal_ids = journal_ids
            var analytic_ids = [];
            var analytic_list = $(".analytic-multiple").select2('data')
            for (var i = 0; i < analytic_list.length; i++) {
                analytic_ids.push(parseInt(analytic_list[i].id))
            }
            output.analytic_ids = analytic_ids
            var analytic_tag_ids = [];
            var analytic_tag_list = $(".analytic-tag-multiple").select2('data')
            for (var i = 0; i < analytic_tag_list.length; i++) {
                analytic_tag_ids.push(parseInt(analytic_tag_list[i].id))
            }
            output.analytic_tag_ids = analytic_tag_ids
            var options_list = $(".extra-multiple").select2('data')
            for (var i = 0; i < options_list.length; i++) {
                if (options_list[i].id === 'debit_credit') {
                    output.debit_credit = true;
                }
            }
            self._rpc({
                model: 'ins.financial.report',
                method: 'write',
                args: [self.wizard_id, output],
            }).then(function (res) {
                self.plot_data(self.initial_render);
            });
        },
    });
    core.action_registry.add('dynamic.fr.pr', DynamicPrMain)
})