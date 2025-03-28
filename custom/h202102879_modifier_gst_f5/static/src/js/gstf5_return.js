odoo.define('h202102879_modifier_gst_f5.gstf5_return', function (require) {
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
    var GstF5ReturnMain = AbstractAction.extend({
        template: 'GstF5ReturnMain',
        events: {
            'click #filter_apply_button': 'update_with_filter',
            'click .move_line': 'view_move_line_form',
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
                    model: 'account.gstreturn',
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
        view_move_line_form: function (event) {
            event.preventDefault();
            var self = this;
            var context = {};
            var redirect_to_document = function (res_model, res_id, view_id) {
                var action = {
                    type: 'ir.actions.act_window',
                    view_type: 'form',
                    view_mode: 'form',
                    res_model: res_model,
                    views: [[false, 'form']],
                    res_id: res_id,
                    target: 'current',
                };
                return self.do_action(action);
            };
            redirect_to_document('account.move', $(event.currentTarget).data('move-id'));
        },
        formatWithSign: function (amount, formatOptions, sign) {
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
            self.loader_disable_ui();
            var node = self.$('.py-data-container-orig');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'account.gstreturn',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterGstF5Return', {get_info: datas,}));
                    self.$el.find('#date_from').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('#date_to').datepicker({dateFormat: 'dd-mm-yy'});
                }
                self.$('.py-data-container-orig').html(QWeb.render('GstF5ReturnMainList', {
                    get_info: datas,
                }));
                self.loader_enable_ui();
            });
        },
        ageing_lines_by_page: function (offset, account_id) {
            var self = this;
            return self._rpc({
                model: 'ins.partner.ageing',
                method: 'process_detailed_data',
                args: [self.wizard_id, offset, account_id],
            })
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
                    k.date_maturity = field_utils.format.date(field_utils.parse.date(k.date_maturity, {}, {isUTC: true}));
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
                        k.date_maturity = field_utils.format.date(field_utils.parse.date(k.date_maturity, {}, {isUTC: true}));
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
        print_pdf: function (e) {
            e.preventDefault();
            var self = this;
            var checkbox1_box7 = false
            var checkbox2_box7 = false
            var checkbox3_box7 = false
            var checkbox1_box8 = false
            var checkbox2_box8 = false
            if ($('#checkbox1-box7-yes')[0].checked) {
                checkbox1_box7 = true
            }
            if ($('#checkbox2-box7-yes')[0].checked) {
                checkbox2_box7 = true
            }
            if ($('#checkbox3-box7-yes')[0].checked) {
                checkbox3_box7 = true
            }
            if ($('#checkbox1-box8-yes')[0].checked) {
                checkbox1_box8 = true
            }
            if ($('#checkbox2-box8-yes')[0].checked) {
                checkbox2_box8 = true
            }
            var context = {
                'checkbox1_box7' : checkbox1_box7,
                'checkbox2_box7' : checkbox2_box7,
                'checkbox3_box7' : checkbox3_box7,
                'checkbox1_box8' : checkbox1_box8,
                'checkbox2_box8' : checkbox2_box8,
                'input1_box7' : $('#input1-box7')[0].value,
                'input2_box7' : $('#input2-box7')[0].value,
                'input3_box7' : $('#input3-box7')[0].value,
                'input1_box8' : $('#input1-box8')[0].value,
                'input2_box8' : $('#input2-box8')[0].value,
            }

            self._rpc({
                model: 'account.gstreturn',
                method: 'check_report',
                args: [[self.wizard_id]],
                context: context,
            }).then(function (action) {
                action['context'] = {
                    'active_model': 'account.gstreturn',
                    'active_id': self.wizard_id,
                }
                return self.do_action(action);
            });
        },
        print_xlsx: function () {
            var self = this;
            self._rpc({
                model: 'account.gstreturn',
                method: 'action_xlsx',
                args: [[self.wizard_id]],
            }).then(function (action) {
                action.context.active_ids = [self.wizard_id];
                return self.do_action(action);
            });
        },
        view_move_line: function (event) {
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
            redirect_to_document('account.move', $(event.currentTarget).data('move-id'));
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
        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = true;
            var output = {date_from: false, date_to: false};
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

            if (output.date_to && output.date_to) {
                self._rpc({
                    model: 'account.gstreturn',
                    method: 'write',
                    args: [self.wizard_id, output],
                }).then(function (res) {
                    self.plot_data(self.initial_render);
                });
            }
        },
    });

    core.action_registry.add('gstf5.return', GstF5ReturnMain);

    return {
        GstF5ReturnMain: GstF5ReturnMain,
    };
});
