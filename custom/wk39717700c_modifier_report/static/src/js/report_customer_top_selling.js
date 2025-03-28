odoo.define('wk39717700c_modifier_report.CustomerTopSellingReport', function (require) {
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
    var CustomerTopSellingReport = AbstractAction.extend({
        template: 'TempCustomerTopSellingReport',
        events: {
            'click #filter_apply_button': 'update_with_filter',
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
                    model: 'report.customer.top.selling',
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
                model: 'report.customer.top.selling',
                method: 'get_data_report',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterCustomerTopSellingReport', {get_info: datas}));
                    self.$el.find('.partner-multiple').select2({
                        placeholder: 'Select Customer...',
                    });
                    self.$el.find('.user-multiple').select2({
                        placeholder: 'Select Salesman...',
                    });
                }
                self.$('.py-data-container-orig').html(QWeb.render('TempCustomerTopSellingReportMain', {
                    get_info: datas,
                }));
                self.loader_enable_ui();
            });
        },
        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {};

            if ($("#date_from").val()) {
                output['start_date'] = self.$el.find('#date_from').val();
            }

            if ($("#date_to").val()) {
                output['end_date'] = self.$el.find('#date_to').val();;
            }
            var partner_list = $(".partner-multiple").select2('data')
            if (partner_list.length > 0){
                var partner_ids = [];
                for (var i = 0; i < partner_list.length; i++) {
                    partner_ids.push(parseInt(partner_list[i].id))
                }
                output.partner_ids = partner_ids
            }
            var user_list = $(".user-multiple").select2('data')
            if (user_list.length > 0) {
                var user_ids = [];
                for (var i = 0; i < user_list.length; i++) {
                    user_ids.push(parseInt(user_list[i].id))
                }
                output.user_ids = user_ids
            }

            self._rpc({
                model: 'report.customer.top.selling',
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
                model: 'report.customer.top.selling',
                method: 'export_report',
                args: [[self.wizard_id]],
            }).then(function (action) {
                action['context'] = {
                    'active_model': 'report.customer.top.selling',
                    'active_id': self.wizard_id,
                }
                return self.do_action(action);
            });
        },
        print_xlsx: function () {
            var self = this;
            self._rpc({
                model: 'report.customer.top.selling',
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

    core.action_registry.add('report.customer.top.selling', CustomerTopSellingReport);

    return {
        CustomerTopSellingReport: CustomerTopSellingReport,
    };
});
