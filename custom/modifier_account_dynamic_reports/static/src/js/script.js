odoo.define('modifier_account_dynamic_reports.dynamic_reports', function (require) {
    "use strict";

    var core = require('web.core');
    var DynamicTbMain = require('account_dynamic_reports.DynamicTbMain');
    var field_utils = require('web.field_utils');
    var QWeb = core.qweb;

    var _t = core._t;

    DynamicTbMain.DynamicGlMain.include({
        events: {
            'click #filter_apply_button': 'update_with_filter',
            'click #pdf': 'print_pdf',
            'click #xlsx': 'print_xlsx',
            'click .view-source': 'view_move_line',
            'click .view-payment': 'view_payment',
            'click .py-mline': 'fetch_move_lines',
            'click .py-mline-page': 'fetch_move_lines_by_page'
        },

        view_payment: function (event) {
            event.preventDefault();
            var self = this;
            var context = {};
            var redirect_to_document = function (res_model, res_id, view_id) {
                var action = {
                    type: 'ir.actions.act_window',
                    view_type: 'form',
                    view_mode: 'form',
                    res_model: res_model,
                    views: [[view_id || false, 'form']],
                    res_id: res_id,
                    target: 'current',
                    context: context,
                };
                self.do_notify(_("Redirected"), "Window has been redirected");
                return self.do_action(action);
            };
            redirect_to_document('multiple.payments', $(event.currentTarget).data('payment-id'));
        },

        change_date_format: function (date_string) {
            var date = ''
            if (date_string) {
                var date_list = date_string.split('-')
                date = date_list[2] + "-" + date_list[1] + "-" + date_list[0]
            }
            return date
        },

        plot_data: function (initial_render = true) {
            var self = this;
            self.loader_disable_ui();
            var node = self.$('.py-data-container-orig');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.general.ledger',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas[0]
                self.account_data = datas[1]
                _.each(self.account_data, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.ldate = field_utils.format.date(field_utils.parse.date(k.ldate, {}, {isUTC: true}));
                    _.each(k.lines, function (ks, vs) {
                        ks.debit = self.formatWithSign(ks.debit, formatOptions, ks.debit < 0 ? '-' : '');
                        ks.credit = self.formatWithSign(ks.credit, formatOptions, ks.credit < 0 ? '-' : '');
                        ks.balance = self.formatWithSign(ks.balance, formatOptions, ks.balance < 0 ? '-' : '');
                        ks.ldate = field_utils.format.date(field_utils.parse.date(ks.ldate, {}, {isUTC: true}));
                    });
                });
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterSection', {
                        filter_data: datas[0],
                    }));
                    if (self._title == 'GL View') {
                        var date_from = self.$el.find('#date_from')
                        if (date_from.length > 0) {
                            date_from[0].setAttribute("type","date")
                            var span_after = date_from.parent().find('span')
                            if (span_after.length > 0) {
                                span_after[0].setAttribute("style","display : none")
                            }
                        }
                        var date_to = self.$el.find('#date_to')
                        if (date_to.length > 0) {
                            date_to[0].setAttribute("type","date")
                            var span_after = date_to.parent().find('span')
                            if (span_after.length > 0) {
                                span_after[0].setAttribute("style", "display : none")
                            }
                        }
                    }
                    else {
                        self.$el.find('#date_from').datepicker({dateFormat: 'dd-mm-yy'});
                        self.$el.find('#date_to').datepicker({dateFormat: 'dd-mm-yy'});
                    }

                    self.$el.find('.date_filter-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Date...',
                    });
                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    })
                        .val(['include_details', 'initial_balance', 'bal_not_zero']).trigger('change')
                    ;
                    self.$el.find('.account-multiple').select2({
                        placeholder: 'Select Account...',
                    });
                    self.$el.find('.account-tag-multiple').select2({
                        placeholder: 'Account Tags...',
                    });
                    self.$el.find('.analytic-tag-multiple').select2({
                        placeholder: 'Analytic Tags...',
                    });
                    self.$el.find('.analytic-multiple').select2({
                        placeholder: 'Select Analytic...',
                    });
                    self.$el.find('.journal-multiple').select2({
                        placeholder: 'Select Journal...',
                    });
                }
                var header = "<div style='text-align: center'><p style='font-size: 30px'>"+self.filter_data['company_name']+"</p>" +
                    "<p style='font-size: 18px'><strong>General Ledger</strong><br/><span>From: "+self.change_date_format(self.filter_data['date_from'])+
                    " To: "+self.change_date_format(self.filter_data['date_to'])+"</span></p></div>"
                self.$('.py-data-container-orig').html(header + QWeb.render('DataSection', {
                    account_data: datas[1],
                    filters : datas[0],
                }));
                self.loader_enable_ui();
            });
        },
        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {date_range: false};
            output.display_accounts = 'balance_not_zero';
            output.initial_balance = false;
            output.include_details = false;
            var journal_ids = [];
            var journal_list = $(".journal-multiple").select2('data')
            for (var i = 0; i < journal_list.length; i++) {
                journal_ids.push(parseInt(journal_list[i].id))
            }
            output.journal_ids = journal_ids
            var account_ids = [];
            var account_list = $(".account-multiple").select2('data')
            for (var i = 0; i < account_list.length; i++) {
                account_ids.push(parseInt(account_list[i].id))
            }
            output.account_ids = account_ids
            var account_tag_ids = [];
            var account_tag_list = $(".account-tag-multiple").select2('data')
            for (var i = 0; i < account_tag_list.length; i++) {
                account_tag_ids.push(parseInt(account_tag_list[i].id))
            }
            output.account_tag_ids = account_tag_ids
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
            if ($(".date_filter-multiple").select2('data').length === 1) {
                output.date_range = $(".date_filter-multiple").select2('data')[0].id
            }
            var options_list = $(".extra-multiple").select2('data')
            for (var i = 0; i < options_list.length; i++) {
                if (options_list[i].id === 'initial_balance') {
                    output.initial_balance = true;
                }
                if (options_list[i].id === 'bal_not_zero') {
                    output.display_accounts = 'balance_not_zero';
                }
                if (options_list[i].id === 'include_details') {
                    output.include_details = true;
                }
            }
            if (self._title == 'GL View') {
                if (self.$el.find('#date_from').val()) {
                    output.date_from = self.$el.find('#date_from').val();
                }
                if (self.$el.find('#date_to').val()) {
                    output.date_to = self.$el.find('#date_to').val();
                }
            }
            else {
                if ($("#date_from").val()) {
                    var dateObject = $("#date_from").datepicker("getDate");
                    var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                    output.date_from = dateString;
                }
                if ($("#date_to").val()) {
                    var dateObject = $("#date_to").datepicker("getDate");
                    var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                    output.date_to = dateString;
                }
            }

            if ($("#date").is(':checked')){
                output.show_date = true
            }
            else {
                output.show_date = false
            }

            if ($("#jrnl").is(':checked')){
                output.show_jrnl = true
            }
            else {
                output.show_jrnl = false
            }

            if ($("#partner").is(':checked')){
                output.show_partner = true
            }
            else {
                output.show_partner = false
            }

            if ($("#move").is(':checked')){
                output.show_move = true
            }
            else {
                output.show_move = false
            }

            if ($("#entry_label").is(':checked')){
                output.show_entry_label = true
            }
            else {
                output.show_entry_label = false
            }

            if ($("#reference").is(':checked')){
                output.show_reference = true
            }
            else {
                output.show_reference = false
            }

            if ($("#remarks").is(':checked')){
                output.show_remarks = true
            }
            else {
                output.show_remarks = false
            }

            if ($("#debit").is(':checked')){
                output.show_debit = true
            }
            else {
                output.show_debit = false
            }

            if ($("#credit").is(':checked')){
                output.show_credit = true
            }
            else {
                output.show_credit = false
            }

            if ($("#debit_fc").is(':checked')){
                output.show_debit_fc = true
            }
            else {
                output.show_debit_fc = false
            }

            if ($("#credit_fc").is(':checked')){
                output.show_credit_fc = true
            }
            else {
                output.show_credit_fc = false
            }

            if ($("#balance").is(':checked')){
                output.show_balance = true
            }
            else {
                output.show_balance = false
            }

            if ($("#balance_in_fc").is(':checked')){
                output.show_balance_in_fc = true
            }
            else {
                output.show_balance_in_fc = false
            }

            if ($("#project_name").is(':checked')){
                output.show_project_name = true
            }
            else {
                output.show_project_name = false
            }

            self._rpc({
                model: 'ins.general.ledger',
                method: 'write',
                args: [[self.wizard_id], output],
            }).then(function (res) {
                self.plot_data(self.initial_render);
            });
        },
    });

    DynamicTbMain.DynamicPlMain.include({
        change_date_format: function (date_string) {
            var date = ''
            if (date_string) {
                var date_list = date_string.split('-')
                date = date_list[2] + "-" + date_list[1] + "-" + date_list[0]
            }
            return date
        },
        plot_data: function (initial_render = true) {
            var self = this;
            self.loader_disable_ui();
            var node = self.$('.py-data-container-orig');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.partner.ledger',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas[0]
                self.account_data = datas[1]
                _.each(self.account_data, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.ldate = field_utils.format.date(field_utils.parse.date(k.ldate, {}, {isUTC: true}));
                    _.each(k.lines, function (ks, vs) {
                        ks.debit = self.formatWithSign(ks.debit, formatOptions, ks.debit < 0 ? '-' : '');
                        ks.credit = self.formatWithSign(ks.credit, formatOptions, ks.credit < 0 ? '-' : '');
                        ks.balance = self.formatWithSign(ks.balance, formatOptions, ks.balance < 0 ? '-' : '');
                        ks.ldate = field_utils.format.date(field_utils.parse.date(ks.ldate, {}, {isUTC: true}));
                    });
                });
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterSectionPl', {
                        filter_data: datas[0],
                    }));
                    self.$el.find('#date_from').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('#date_to').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('.date_filter-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Date...',
                    });
                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    })
                        .val(['include_details', 'initial_balance']).trigger('change');
                    self.$el.find('.type-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Account Type...',
                    });
                    self.$el.find('.reconciled-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Reconciled...',
                    });
                    self.$el.find('.partner-multiple').select2({
                        placeholder: 'Select Partner...',
                    });
                    self.$el.find('.partner-tag-multiple').select2({
                        placeholder: 'Select Tag...',
                    });
                    self.$el.find('.account-multiple').select2({
                        placeholder: 'Select Account...',
                    });
                    self.$el.find('.journal-multiple').select2({
                        placeholder: 'Select Journal...',
                    });
                }
                var header = "<div style='text-align: center'><p style='font-size: 30px'>"+self.filter_data['company_name']+"</p>" +
                    "<p style='font-size: 18px'><strong>Partner Ledger</strong><br/><span>From: "+self.change_date_format(self.filter_data['date_from'])+
                    " To: "+self.change_date_format(self.filter_data['date_to'])+"</span></p></div>"
                self.$('.py-data-container-orig').html(header + QWeb.render('DataSectionPl', {
                    account_data: datas[1]
                }));
                self.loader_enable_ui();
            });
        },
    });

    DynamicTbMain.DynamicTbMain.include({
        plot_data: function (initial_render = true) {
            var self = this;
            var node = self.$('.py-data-container');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.trial.balance',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas[0];
                self.account_data = datas[1];
                self.retained = datas[2];
                self.subtotal = datas[3];
                _.each(self.account_data, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.initial_debit = self.formatWithSign(k.initial_debit, formatOptions, k.initial_debit < 0 ? '-' : '');
                    k.initial_credit = self.formatWithSign(k.initial_credit, formatOptions, k.initial_credit < 0 ? '-' : '');
                    k.initial_balance = self.formatWithSign(k.initial_balance, formatOptions, k.initial_balance < 0 ? '-' : '');
                    k.ending_debit = self.formatWithSign(k.ending_debit, formatOptions, k.ending_debit < 0 ? '-' : '');
                    k.ending_credit = self.formatWithSign(k.ending_credit, formatOptions, k.ending_credit < 0 ? '-' : '');
                    k.ending_balance = self.formatWithSign(k.ending_balance, formatOptions, k.ending_balance < 0 ? '-' : '');
                });
                _.each(self.retained, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.initial_debit = self.formatWithSign(k.initial_debit, formatOptions, k.initial_debit < 0 ? '-' : '');
                    k.initial_credit = self.formatWithSign(k.initial_credit, formatOptions, k.initial_credit < 0 ? '-' : '');
                    k.initial_balance = self.formatWithSign(k.initial_balance, formatOptions, k.initial_balance < 0 ? '-' : '');
                    k.ending_debit = self.formatWithSign(k.ending_debit, formatOptions, k.ending_debit < 0 ? '-' : '');
                    k.ending_credit = self.formatWithSign(k.ending_credit, formatOptions, k.ending_credit < 0 ? '-' : '');
                    k.ending_balance = self.formatWithSign(k.ending_balance, formatOptions, k.ending_balance < 0 ? '-' : '');
                });
                _.each(self.subtotal, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.initial_debit = self.formatWithSign(k.initial_debit, formatOptions, k.initial_debit < 0 ? '-' : '');
                    k.initial_credit = self.formatWithSign(k.initial_credit, formatOptions, k.initial_credit < 0 ? '-' : '');
                    k.initial_balance = self.formatWithSign(k.initial_balance, formatOptions, k.initial_balance < 0 ? '-' : '');
                    k.ending_debit = self.formatWithSign(k.ending_debit, formatOptions, k.ending_debit < 0 ? '-' : '');
                    k.ending_credit = self.formatWithSign(k.ending_credit, formatOptions, k.ending_credit < 0 ? '-' : '');
                    k.ending_balance = self.formatWithSign(k.ending_balance, formatOptions, k.ending_balance < 0 ? '-' : '');
                });
                self.filter_data.date_from_tmp = self.filter_data.date_from;
                self.filter_data.date_to_tmp = self.filter_data.date_to;
                self.filter_data.date_from = field_utils.format.date(field_utils.parse.date(self.filter_data.date_from, {}, {isUTC: true}));
                self.filter_data.date_to = field_utils.format.date(field_utils.parse.date(self.filter_data.date_to, {}, {isUTC: true}));
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterSectionTb', {
                        filter_data: self.filter_data,
                    }));
                    self.$el.find('#date_from').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('#date_to').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('.date_filter-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Date...',
                    });
                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    }).val('bal_not_zero').trigger('change');
                    self.$el.find('.analytic-multiple').select2({
                        placeholder: 'Select Analytic...',
                    });
                    self.$el.find('.journal-multiple').select2({
                        placeholder: 'Select Journal...',
                    });
                }
                var header = "<div style='text-align: center'><p style='font-size: 30px'>"+self.filter_data['company_name']+"</p>" +
                    "<p style='font-size: 18px'><strong>Trial Balance</strong><br/><span>From: "+self.filter_data['date_from']+
                    " To: "+self.filter_data['date_to']+"</span></p></div>"
                self.$('.py-data-container').html(header + QWeb.render('DataSectionTb', {
                    account_data: self.account_data,
                    retained: self.retained,
                    subtotal: self.subtotal,
                    filter_data: self.filter_data,
                }));
            });
        },
    });

    DynamicTbMain.DynamicPaMain.include({
        events: _.extend({}, DynamicTbMain.DynamicPaMain.prototype.events, {
            'click #expand_all': '_onClickExpandAll',
            'click #unexpand_all': '_onClickUnExpandAll'
        }),
        click_fetch_move_lines: function (tr_line) {
            var self = this;
            var partner_id = tr_line.data('partner-id');
            var offset = 0;
            var td = tr_line.next('tr').find('td');
            if (td.length == 1) {
                self.loader_disable_ui();
                self.ageing_lines_by_page(offset, partner_id).then(function (datas) {
                    var count = datas[0];
                    var offset = datas[1];
                    var account_data = datas[2];
                    var period_list = datas[3];
                    _.each(account_data, function (k, v) {
                        var formatOptions = {
                            currency_id: k.company_currency_id,
                            noSymbol: true,
                        };
                        k.range_0 = self.formatWithSign(k.range_0, formatOptions, k.range_0 < 0 ? '-' : '');
                        k.range_1 = self.formatWithSign(k.range_1, formatOptions, k.range_1 < 0 ? '-' : '');
                        k.range_2 = self.formatWithSign(k.range_2, formatOptions, k.range_2 < 0 ? '-' : '');
                        k.range_3 = self.formatWithSign(k.range_3, formatOptions, k.range_3 < 0 ? '-' : '');
                        k.range_4 = self.formatWithSign(k.range_4, formatOptions, k.range_4 < 0 ? '-' : '');
                        k.range_5 = self.formatWithSign(k.range_5, formatOptions, k.range_5 < 0 ? '-' : '');
                        k.range_6 = self.formatWithSign(k.range_6, formatOptions, k.range_6 < 0 ? '-' : '');
                        k.range_7 = self.formatWithSign(k.range_7, formatOptions, k.range_7 < 0 ? '-' : '');
                        k.date_maturity = field_utils.format.date(field_utils.parse.date(k.date_maturity, {}, {isUTC: true}));
                        k.date = field_utils.format.date(field_utils.parse.date(k.date, {}, {isUTC: true}));
                    });
                    tr_line.next('tr').find('td .py-mline-table-div').remove();
                    tr_line.next('tr').find('td ul').after(
                        QWeb.render('SubSectionPa', {
                            count: count,
                            offset: offset,
                            account_data: account_data,
                            period_list: period_list
                        }))
                    tr_line.next('tr').find('td ul li:first a').css({
                        'background-color': '#00ede8',
                        'font-weight': 'bold',
                    });
                    self.loader_enable_ui();
                })
            }
        },
        _onClickExpandAll: function (event) {
            var data_lines = $("#data-lines").find(".py-mline")
            var count = 0
            var self = this;
            _.each(data_lines, function(line) {
                if (line.getAttribute('aria-expanded') != 'true' && count <= 50) {
                    count = count + 1
                    var tr_line = $('tr[data-partner-id='+ line.getAttribute('data-partner-id') +']');
                    tr_line.trigger("click");
                    self.click_fetch_move_lines(tr_line)
                }
            });
        },
        _onClickUnExpandAll: function (event) {
            var data_lines = $("#data-lines").find(".py-mline")
            var count = 0
            _.each(data_lines, function(line) {
                if (line.getAttribute('aria-expanded') == 'true' && count <= 500) {
                    count = count + 1
                    var tr_line = $('tr[data-partner-id='+ line.getAttribute('data-partner-id') +']');
                    tr_line.trigger("click");
                }
            });
        },
        change_date_format: function (date_string) {
            var date = ''
            if (date_string) {
                var date_list = date_string.split('-')
                date = date_list[2] + "-" + date_list[1] + "-" + date_list[0]
            }
            return date
        },
        plot_data: function (initial_render = true) {
            var self = this;
            self.loader_disable_ui();
            var node = self.$('.py-data-container-orig');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.partner.ageing',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas[0]
                self.ageing_data = datas[1]
                self.period_dict = datas[2]
                self.period_list = datas[3]
                _.each(self.ageing_data, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    for (var z = 0; z < self.period_list.length; z++) {
                        k[self.period_list[z]] = self.formatWithSign(k[self.period_list[z]], formatOptions, k[self.period_list[z]] < 0 ? '-' : '');
                    }
                    k.total = self.formatWithSign(k.total, formatOptions, k.total < 0 ? '-' : '');
                });
                if (initial_render) {
                    var titel = "Partner Ageing"
                    if (self._title) {
                        titel = self._title
                    }
                    var header = "<div style='text-align: center;border-top:1px solid #cccccc;margin-top: 10px'><p style='font-size: 30px'>"+self.filter_data['company_name']+"</p>" +
                    "<p style='font-size: 18px'><strong>"+titel+"</strong><br/><span>As on date: "+self.change_date_format(self.filter_data['as_on_date'])+"</span></p></div>"

                    self.$('.py-control-panel').html(QWeb.render('FilterSectionPa', {
                        filter_data: self.filter_data,
                    }) + header);
                    self.$el.find('#as_on_date').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('.type-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Account Type...',
                    });
                    self.$el.find('.partner-type-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Partner Type...',
                    });
                    self.$el.find('.partner-multiple').select2({
                        placeholder: 'Select Partner...',
                    });
                    self.$el.find('.partner-tag-multiple').select2({
                        placeholder: 'Select Tag...',
                    });
                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    })
                        .val('include_details').trigger('change')
                    ;
                }

                self.$('.py-data-container-orig').html(QWeb.render('DataSectionPa', {
                    ageing_data: self.ageing_data,
                    period_dict: self.period_dict,
                    period_list: self.period_list
                }));
                self.$('.py-breadcrumb').html("<li>"+titel+"</li>");
                self.loader_enable_ui();
            });
        },
        fetch_move_lines_by_page: function (event) {
            event.preventDefault();
            var self = this;
            var partner_id = $(event.currentTarget).data('partner-id');
            var offset = parseInt($(event.currentTarget).data('page-number')) - 1;
            var total_rows = parseInt($(event.currentTarget).data('count'));
            self.loader_disable_ui();
            self.ageing_lines_by_page(offset, partner_id).then(function (datas) {
                var count = datas[0];
                var offset = datas[1];
                var account_data = datas[2];
                var period_list = datas[3];
                _.each(account_data, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.range_0 = self.formatWithSign(k.range_0, formatOptions, k.range_0 < 0 ? '-' : '');
                    k.range_1 = self.formatWithSign(k.range_1, formatOptions, k.range_1 < 0 ? '-' : '');
                    k.range_2 = self.formatWithSign(k.range_2, formatOptions, k.range_2 < 0 ? '-' : '');
                    k.range_3 = self.formatWithSign(k.range_3, formatOptions, k.range_3 < 0 ? '-' : '');
                    k.range_4 = self.formatWithSign(k.range_4, formatOptions, k.range_4 < 0 ? '-' : '');
                    k.range_5 = self.formatWithSign(k.range_5, formatOptions, k.range_5 < 0 ? '-' : '');
                    k.range_6 = self.formatWithSign(k.range_6, formatOptions, k.range_6 < 0 ? '-' : '');
                    k.range_7 = self.formatWithSign(k.range_7, formatOptions, k.range_7 < 0 ? '-' : '');
                    k.date_maturity = field_utils.format.date(field_utils.parse.date(k.date_maturity, {}, {isUTC: true}));
                    k.date = field_utils.format.date(field_utils.parse.date(k.date, {}, {isUTC: true}));
                });
                $(event.currentTarget).parent().parent().parent().find('.py-mline-table-div').remove();
                $(event.currentTarget).parent().parent().find('a').css({
                    'background-color': 'white',
                    'font-weight': 'normal'
                });
                $(event.currentTarget).parent().parent().after(
                    QWeb.render('SubSectionPa', {
                        count: count,
                        offset: offset,
                        account_data: account_data,
                        period_list: period_list
                    }));
                $(event.currentTarget).css({
                    'background-color': '#00ede8',
                    'font-weight': 'bold',
                });
                self.loader_enable_ui()
            })
        },
        fetch_move_lines: function (event) {
            event.preventDefault();
            var self = this;
            var partner_id = $(event.currentTarget).data('partner-id');
            var offset = 0;
            var td = $(event.currentTarget).next('tr').find('td');
            if (td.length == 1) {
                self.loader_disable_ui();
                self.ageing_lines_by_page(offset, partner_id).then(function (datas) {
                    var count = datas[0];
                    var offset = datas[1];
                    var account_data = datas[2];
                    var period_list = datas[3];
                    _.each(account_data, function (k, v) {
                        var formatOptions = {
                            currency_id: k.company_currency_id,
                            noSymbol: true,
                        };
                        k.range_0 = self.formatWithSign(k.range_0, formatOptions, k.range_0 < 0 ? '-' : '');
                        k.range_1 = self.formatWithSign(k.range_1, formatOptions, k.range_1 < 0 ? '-' : '');
                        k.range_2 = self.formatWithSign(k.range_2, formatOptions, k.range_2 < 0 ? '-' : '');
                        k.range_3 = self.formatWithSign(k.range_3, formatOptions, k.range_3 < 0 ? '-' : '');
                        k.range_4 = self.formatWithSign(k.range_4, formatOptions, k.range_4 < 0 ? '-' : '');
                        k.range_5 = self.formatWithSign(k.range_5, formatOptions, k.range_5 < 0 ? '-' : '');
                        k.range_6 = self.formatWithSign(k.range_6, formatOptions, k.range_6 < 0 ? '-' : '');
                        k.range_7 = self.formatWithSign(k.range_7, formatOptions, k.range_7 < 0 ? '-' : '');
                        k.date_maturity = field_utils.format.date(field_utils.parse.date(k.date_maturity, {}, {isUTC: true}));
                        k.date = field_utils.format.date(field_utils.parse.date(k.date, {}, {isUTC: true}));
                    });
                    $(event.currentTarget).next('tr').find('td .py-mline-table-div').remove();
                    $(event.currentTarget).next('tr').find('td ul').after(
                        QWeb.render('SubSectionPa', {
                            count: count,
                            offset: offset,
                            account_data: account_data,
                            period_list: period_list
                        }))
                    $(event.currentTarget).next('tr').find('td ul li:first a').css({
                        'background-color': '#00ede8',
                        'font-weight': 'bold',
                    });
                    self.loader_enable_ui();
                })
            }
        },
    });

    DynamicTbMain.DynamicFrMain.include({
        change_date_format: function (date_string) {
            var date = ''
            if (date_string) {
                var date_list = date_string.split('-')
                date = date_list[2] + "-" + date_list[1] + "-" + date_list[0]
            }
            return date
        },

        plot_data: function (initial_render = true) {
            var self = this;
            var node = self.$('.py-data-container');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.financial.report',
                method: 'get_report_values',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas.form;
                self.account_data = datas.report_lines;
                var formatOptions = {
                    currency_id: datas.currency,
                    noSymbol: true,
                };
                var balance_cmp_list = datas.form.balance_cmp_list
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
                    _.each(balance_cmp_list, function (balance_cmp) {
                        k[balance_cmp] = self.formatWithSign(k[balance_cmp], formatOptions, k[balance_cmp] < 0 ? '-' : '');
                    })
                });
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterSectionFr', {
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
                if (self.filter_data['date_from_cmp'] && self.filter_data['date_to_cmp']) {
                    var header = "<div style='text-align: center'><p style='font-size: 30px'>"+self.filter_data['company_id'][1]+"</p>" +
                    "<p style='font-size: 18px'><strong>"+self.filter_data['account_report_id'][1]+"</strong><br/><span>From: "+self.change_date_format(self.filter_data['date_from_cmp'])+
                    " To: "+self.change_date_format(self.filter_data['date_to_cmp'])+"</span></p></div>"
                }
                else {
                    var header = "<div style='text-align: center'><p style='font-size: 30px'>"+self.filter_data['company_id'][1]+"</p>" +
                    "<p style='font-size: 18px'><strong>"+self.filter_data['account_report_id'][1]+"</strong><br/><span>From: "+self.change_date_format(self.filter_data['date_from'])+
                    " To: "+self.change_date_format(self.filter_data['date_to'])+"</span></p></div>"
                }
                self.$('.py-data-container').html(header + QWeb.render('DataSectionFr', {
                    account_data: self.account_data,
                    filter_data: self.filter_data,
                }));
                if (parseFloat(datas.initial_balance) > 0 || parseFloat(datas.current_balance) > 0 || parseFloat(datas.ending_balance) > 0) {
                    $(".py-data-container").append(QWeb.render('SummarySectionFr', {
                        initial_balance: self.initial_balance,
                        current_balance: self.current_balance,
                        ending_balance: self.ending_balance
                    }));
                }
            });
        },
        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {date_range: false, enable_filter: false, debit_credit: false, hide_line: false,
                date_from_cmp: false, date_to_cmp:false, comp_period: false, comp_month_year_selection: false, enable_month_year_comp: false};
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

            if ($("#number_of_comparison").val()) {
                output.number_of_comparison = $("#number_of_comparison").val()
                output.enable_filter = true;
            }

            if ($("#comparison_number_of_month").val()) {
                output.comp_period = $("#comparison_number_of_month").val()
                output.comp_month_year_selection = 'month'
                output.enable_month_year_comp = true;
            }

            if ($("#comparison_number_of_year").val()) {
                output.comp_period = $("#comparison_number_of_year").val()
                output.comp_month_year_selection = 'year'
                output.enable_month_year_comp = true;
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
                if (options_list[i].id === 'hide_line') {
                    output.hide_line = true;
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

});