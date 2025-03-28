odoo.define('f53167513x_modifier_register_payment.payment', function (require) {
    "use strict";

    var AccountPayment = require('account.payment');

    AccountPayment.ShowPaymentLineWidget.include({
        _onOpenPayment: function (event) {
            var self = this
            var paymentId = parseInt($(event.target).attr('payment-id'));
            var moveId = parseInt($(event.target).attr('move-id'));
            var res_model;
            var id;
            if (paymentId !== undefined && !isNaN(paymentId)){
                res_model = "account.payment";
                id = paymentId;
            } else if (moveId !== undefined && !isNaN(moveId)){
                res_model = "account.move";
                id = moveId;
            }
            //Open form view of account.move with id = move_id
            if (res_model && id) {
                this._rpc({
                    model: 'account.move',
                    method: 'get_open_payment',
                    args: [[], res_model, id],
                    }).then(function (result) {
                        self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: result[0],
                            res_id: result[1],
                            views: [[false, 'form']],
                            context: {
                                'view_payment': true,
                            },
                            target: 'current'
                        });
                });
            }
        },
    })
})