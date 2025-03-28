odoo.define('modifier_gl_account_dynamic_reports.GLreports', function (require) {
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
        view_move_line: function (event) {
            event.preventDefault();
            var self = this;
            var redirect_to_document = function (res_model, res_id, view_id) {
                var url = '/web#id='+ res_id +'&model=' + res_model + '&view_type=form'
                self.do_notify(_("Redirected"), "Window has been redirected");
                return self.do_action({
                    type: 'ir.actions.act_url',
                    target: 'new',
                    url: url,
                });
            };
            redirect_to_document('account.move', $(event.currentTarget).data('move-id'));
        },
        fetch_move_lines_by_page: function (event) {
            event.preventDefault();
            var self = this;
            var account_id = $(event.currentTarget).data('account-id');
            var offset = parseInt($(event.currentTarget).data('page-number')) - 1;
            var total_rows = parseInt($(event.currentTarget).data('count'));
            self.loader_disable_ui();
            self.gl_lines_by_page(offset, account_id).then(function (datas) {
                _.each(datas[2], function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                    k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                    k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                    k.ldate = field_utils.format.date(field_utils.parse.date(k.ldate, {}, {isUTC: true}));
                });
                $(event.currentTarget).parent().parent().parent().find('.py-mline-table-div').remove();
                $(event.currentTarget).parent().parent().find('a').css({
                    'background-color': 'white',
                    'font-weight': 'normal'
                });
                $(event.currentTarget).parent().parent().after(
                    QWeb.render('SubSection', {
                        count: datas[0],
                        offset: datas[1],
                        account_data: datas[2],
                        filters: datas[3],
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
            var account_id = $(event.currentTarget).data('account-id');
            var offset = 0;
            var td = $(event.currentTarget).next('tr').find('td');
            if (td.length == 1) {
                self.loader_disable_ui();
                self.gl_lines_by_page(offset, account_id).then(function (datas) {
                    _.each(datas[2], function (k, v) {
                        var formatOptions = {
                            currency_id: k.company_currency_id,
                            noSymbol: true,
                        };
                        k.debit = self.formatWithSign(k.debit, formatOptions, k.debit < 0 ? '-' : '');
                        k.credit = self.formatWithSign(k.credit, formatOptions, k.credit < 0 ? '-' : '');
                        k.balance = self.formatWithSign(k.balance, formatOptions, k.balance < 0 ? '-' : '');
                        k.ldate = field_utils.format.date(field_utils.parse.date(k.ldate, {}, {isUTC: true}));
                    });
                    $(event.currentTarget).next('tr').find('td .py-mline-table-div').remove();
                    $(event.currentTarget).next('tr').find('td ul').after(
                        QWeb.render('SubSection', {
                            count: datas[0],
                            offset: datas[1],
                            account_data: datas[2],
                            filters: datas[3],
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
});