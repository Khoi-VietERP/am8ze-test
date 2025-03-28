odoo.define('modifier_journal_audit_report.JournalAuditMain', function (require) {
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
    var JournalAuditMain = AbstractAction.extend({
        template: 'JournalAuditMainList',
        events: {
            'click #filter_apply_button': 'update_with_filter',
            'click #print_pdf': 'print_pdf',
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
                    model: 'account.print.journal',
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
                model: 'account.print.journal',
                method: 'get_report_html',
                args: [[self.wizard_id]],
            }).then(function (data) {
                self.$('.py-data-container-orig').html(data);
                self.loader_enable_ui();
            });
        },
        print_pdf: function (e) {
            e.preventDefault();
            var self = this;
            self._rpc({
                model: 'account.print.journal',
                method: 'check_report',
                args: [[self.wizard_id]],
            }).then(function (action) {
                action['context'] = {
                    'active_model': 'account.print.journal',
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

    core.action_registry.add('journal.audit', JournalAuditMain);

    return {
        JournalAuditMain: JournalAuditMain,
    };
});
