odoo.define('h202_modifier_payment_widget.payment', function (require) {
    "use strict";

    var AccountPayment = require('account.payment');

    AccountPayment.ShowPaymentLineWidget.include({
        events: _.extend({}, AccountPayment.ShowPaymentLineWidget.prototype.events, {
            'click #outstanding' : '_onReload',
        }),

        _onReload: function (event) {
            this.trigger_up('reload');
        },

        _onOutstandingCreditAssign: function (event) {
            event.stopPropagation();
            event.preventDefault();
            var self = this;
            var id = $(event.target).data('id') || false;

            self.do_action({
                type:'ir.actions.act_window',
                view_mode: 'form',
                target: 'new',
                res_model: 'account.move.reconcile',
                views: [[false, 'form']],
                context: {'default_move_id' : JSON.parse(this.value).move_id, 'default_ml_reconcile_id' : id},
            });
        },
    });
});