odoo.define('alphabricks_modifier_account.payment', function (require) {
    "use strict";

    var AccountPayment = require('account.payment');
    var core = require('web.core');
    var field_utils = require('web.field_utils');

    var QWeb = core.qweb;
    var _t = core._t;

    AccountPayment.ShowPaymentLineWidget.include({
            /**
         * @private
         * @override
         */
        _render: function() {
            var self = this;
            var info = JSON.parse(this.value);
            if (!info) {
                this.$el.html('');
                return;
            }
            _.each(info.content, function (k, v){
                k.index = v;
                k.amount = field_utils.format.float(k.amount, {digits: k.digits});
                if (k.date){
                    k.date = field_utils.format.date(field_utils.parse.date(k.date, {}, {isUTC: true}));
                }
            });
            this.$el.html(QWeb.render('ShowPaymentInfo', {
                lines: info.content,
                outstanding: info.outstanding,
                title: info.title
            }));
            _.each(this.$('.js_payment_info'), function (k, v){
                var isRTL = _t.database.parameters.direction === "rtl";
                var content = info.content[v];
                var options = {
                    content: function () {
                        var $content = $(QWeb.render('PaymentPopOver', {
                            name: content.name,
                            journal_name: content.journal_name,
                            date: content.date,
                            amount: content.amount,
                            currency: content.currency,
                            position: content.position,
                            payment_id: content.payment_id,
                            payment_method_name: content.payment_method_name,
                            move_id: content.move_id,
                            ref: content.ref,
                            account_payment_id: content.account_payment_id,
                        }));
                        $content.filter('.js_unreconcile_payment').on('click', self._onRemoveMoveReconcile.bind(self));
                        $content.filter('.js_open_payment').on('click', self._onOpenPayment.bind(self));
                        $content.filter('.js_open_multi_payment').on('click', self._onOpenMultiPayment.bind(self));
                        return $content;
                    },
                    html: true,
                    placement: isRTL ? 'bottom' : 'left',
                    title: 'Payment Information',
                    trigger: 'focus',
                    delay: { "show": 0, "hide": 100 },
                    container: $(k).parent(), // FIXME Ugly, should use the default body container but system & tests to adapt to properly destroy the popover
                };
                $(k).popover(options);
            });
        },

        _onOpenMultiPayment: function (event) {
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
                        if (result) {
                            self.do_action({
                                type: 'ir.actions.act_window',
                                res_model: result[0],
                                res_id: result[1],
                                views: [[result[2], 'form']],
                                context: {
                                    'view_payment': true,
                                },
                                target: 'current'
                            });
                        }
                        else {
                            self.do_action({
                                type: 'ir.actions.act_window',
                                res_model: res_model,
                                res_id: id,
                                views: [[false, 'form']],
                                target: 'current'
                            });
                        }
                });
            }
        },

            /**
         * @private
         * @override
         * @param {MouseEvent} event
         */
        _onOpenPayment: function (event) {
            var paymentId = parseInt($(event.target).attr('payment-id'));
            var moveId = parseInt($(event.target).attr('move-id'));
            var res_model;
            var id;
            if (moveId !== undefined && !isNaN(moveId)){
                res_model = "account.move";
                id = moveId;
            }
            //Open form view of account.move with id = move_id
            if (res_model && id) {
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: res_model,
                    res_id: id,
                    views: [[false, 'form']],
                    target: 'current'
                });
            }
        },
    })
})