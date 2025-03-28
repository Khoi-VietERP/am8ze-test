odoo.define('daa_datapost.import_button', function(require) {

    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var Sidebar = require('web.Sidebar');
    var ListController = require('web.ListController');
    var framework = require('web.framework');
    var Dialog = require('web.Dialog');


    ListController.include({

        renderButtons: function ($node) {
            // this.ksIsAdmin = odoo.session_info.is_admin;
            // debugger

            this._super.apply(this, arguments);


            if (this.$buttons) {
                var import_button = this.$buttons.find('.invoice_now_button');
                import_button.click(this.proxy('invoice_now_action'));
            }
        },

        invoice_now_action: function(e) {
            var self = this;
            self._rpc({
                    model: 'account.move',
                    method: 'cron_check_income_invoices',
                });
        },
    });
});