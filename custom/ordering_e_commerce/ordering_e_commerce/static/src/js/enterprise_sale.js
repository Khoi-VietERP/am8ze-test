odoo.define('blanket_e_commerce.enterprise_sale', function (require) {
    'use strict';

    var utils = require('web.utils');
    var rpc = require('web.rpc');
    var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');
    var core = require('web.core');
    var config = require('web.config');
    var sAnimations = require('website.content.snippets.animation');

    var _t = core._t;
    var qweb = core.qweb

    var getUrlParameter = function getUrlParameter(sParam) {
        var sPageURL = window.location.search.substring(1),
            sURLVariables = sPageURL.split('&'),
            sParameterName,
            i;

        for (i = 0; i < sURLVariables.length; i++) {
            sParameterName = sURLVariables[i].split('=');

            if (sParameterName[0] === sParam) {
                return typeof sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
            }
        }
        return false;
    };

    sAnimations.registry.EnterpriseWebsiteSale = sAnimations.Class.extend(ProductConfiguratorMixin, {
        selector: '.enterprise_sale',
        read_events: {
            'change .js_quantity': '_onChangeOrderQuantity',
            'click .js_add_cart_json_button': '_onClickOrderQuantity',
            'click .next-steps': '_onClickNextStep',
            'click .address-checkout-confirm': '_onClickCheckoutConfirm',
            'click .address-checkout-back': '_onClickBackCart',
            'click .js_edit_address': '_onClickEditAddress',
            'click .address-form-back': '_onClickBackAddress',
            'click .address-form-submit': '_onClickSubmitEditAddress',
            'click .add-new-address': '_onClickAddAddress',
            'click .js_change_shipping': '_onClickChangeShipping',
            'click .payment-back': '_onClickWizardStep20',
            'click .blanket-order-confirm': '_onClickOrderConfirm',
            'keyup .oe_search_box': '_onOrderFilter',
        },
        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            this.step = 10;
            this._setSteps();
            this.blanket_order = parseInt(getUrlParameter('blanket_order')) || 0;
            this.blanket_order_local = 'blanket_order_' + this.blanket_order;
            this.order_data = JSON.parse(localStorage.getItem(this.blanket_order_local) || '{}');
            this._setData();
            return def;
        },
        displayLoading: function () {
            var msg = _t("We are processing, please wait ...");
            $.blockUI({
                'message': '<h2 class="text-white"><img src="/web/static/src/img/spin.png" class="fa-pulse"/>' +
                    '    <br />' + msg +
                    '</h2>'
            });
        },
        _setData: function() {
            if (_.isEmpty(this.order_data)) {
                this.order_data['order_line'] = {};
                return;
            }
            // set blanket order selected
            if (this.blanket_order) {
                $('select[name="blanket_order"] option[value="'+ this.blanket_order +'"]').attr('selected',true);
                this.order_data['blanket_order_id'] = this.order_data['blanket_order_id'] || parseInt(this.blanket_order);
                this.order_data['order_line'] = this.order_data['order_line'] || {};
                this.order_data['billing_address'] = this.order_data['billing_address'] || -1;
                this.order_data['shipping_address'] = this.order_data['shipping_address'] || -1;
            }
            // load data from local
            // set order line
            _.each(this.order_data['order_line'], function(val, key) {
                var $input = $('input[data-line-id='+ key +']');
                $input.val(val);
                $input.trigger("change");
            });
            // set address
            if (this.order_data['billing_address'] != -1)
                $('.one_kanban[data-id=' + this.order_data['shipping_address'] + '] .js_change_shipping').trigger('click');
            if (this.order_data['shipping_address'] != -1)
                $('.one_kanban[data-id=' + this.order_data['shipping_address'] + '] .js_change_shipping').trigger('click');
            this.setDataLocal();
            this.updateCartSummaryPrice();
        },
        _onClickNextStep: function(e) {
            var self = this;
            this.displayLoading();
            this._rpc({
                route: '/ordering/confirm',
                params: {
                    order: this.order_data,
                },
            }).then(function(result) {
                self.removeDataLocal()
                window.location = result
            });
        },
        _onClickBackCart: function(e) {
            this._onClickWizardStep10(e)
        },
        _onClickWizardStep10: function(e) {
            this.step = 10;
            this._setSteps();
        },
        _onClickWizardStep20: function(e) {
            this.step = 20;
            this._setSteps();
        },
        _onClickWizardStep40: function(e) {
            this.step = 40;
            this._setSteps();
        },
        _setSteps: function() {
            var $all = $('.progress-wizard-step');
            var $step10 = $('#wizard-step10');
            var $step20 = $('#wizard-step20');
            var $enterprise_sale = $('.enterprise_sale');
            $all.removeClass('complete').removeClass('active').addClass('active');
            switch(this.step) {
                case 10:
                    $enterprise_sale.addClass('enterprise_sale_'+this.step).removeClass('enterprise_sale_20').removeClass('enterprise_sale_40');
                    break;
                case 20:
                    $enterprise_sale.addClass('enterprise_sale_'+this.step).removeClass('enterprise_sale_10').removeClass('enterprise_sale_40');
                    $step10.removeClass('active').addClass('complete');
                    break;
                case 40:
                    $enterprise_sale.addClass('enterprise_sale_'+this.step).removeClass('enterprise_sale_10').removeClass('enterprise_sale_20');
                    $step10.removeClass('active').addClass('complete');
                    $step20.removeClass('active').addClass('complete');
                    break;
                default:
                    break;
            }
        },
        _onOrderFilter: function(e) {
            var value = $(e.target).val().toLowerCase();
            if (!value)
                $('.js_cart_lines tbody tr').show();
            console.log('_onOrderFilter >>>>>', value);
            $('.td-product_name .enterprise-sale-search-name:not(:contains('+ value +'))').parents('tr').hide();
            $('.td-product_name .enterprise-sale-search-name:contains('+ value +')').parents('tr').show();
        },
        _onChangeOrderQuantity: function(e) {
            var $target = $(e.target);
            var lineId = $target.data('line-id');
            var $cartLine = $('#cart_products_summary').find('tr[data-line-id='+ lineId +']');
            var current_value = $target.val() && parseInt($target.val()) || 0
            current_value = current_value > 0 ? current_value : 0;
            $target.val(current_value);
            //update Cart Summary
            $cartLine.find('.td-qty').text(current_value);
            // save data
            this.order_data['order_line'][lineId] = current_value;
            // update data to local
            this.setDataLocal();
            this.updateCartSummaryPrice();
        },
        _onClickOrderQuantity: function(e) {
            var $target = $(e.target);
            var is_plus = $target.find('i').hasClass('fa-plus') || $target.hasClass('fa-plus');
            var $input = $target.parents('td').find('input');
            var current_value = parseInt($input.val()) || 0;
            var new_value = is_plus ? current_value + 1 : current_value - 1;
            $input.val(new_value);
            $input.trigger("change");
        },
        setDataLocal: function() {
            localStorage.setItem(this.blanket_order_local, JSON.stringify(this.order_data));
        },
        removeDataLocal: function() {
            localStorage.removeItem(this.blanket_order_local, JSON.stringify(this.order_data));
        },
        updateCartSummaryPrice: function() {
            var $cartProductsSummary = $('#cart_products_summary');
            var lines = $cartProductsSummary.find('tbody tr');
            var sub_total = 0.0;
            var tax_total = 0.0;
            var line_infor = {};
            _.each(lines, function(line) {
                if (!line_infor[$(line).data('line-id')])
                    line_infor[$(line).data('line-id')] = {
                        line_price_unit: $(line).data('line-price_unit'),
                        line_tax: $(line).data('line-tax') || 0,
                        total: 0.0
                    }
                var _qty = parseInt($(line).find('.td-qty').text());
                //calculate line price
                console.log('Updating tax');
                var sub_price = _qty * line_infor[$(line).data('line-id')].line_price_unit;
                var tax_price = sub_price * line_infor[$(line).data('line-id')].line_tax;
                var $line = $(line);
                if (_qty > 0) {
                    $line.show()
                } else {
                    $line.hide()
                };
                $line.find('.td-price .oe_currency_value').text(sub_price.toFixed(2));
                // calculation total
                sub_total += sub_price;
                tax_total += tax_price;
            });
            // update total
            $cartProductsSummary.parent().parent().find('.amount_subtotal .oe_currency_value').text(sub_total.toFixed(2));
            $cartProductsSummary.parent().parent().find('.amount_tax .oe_currency_value').text(tax_total.toFixed(2));
            $cartProductsSummary.parent().parent().find('.amount_total .oe_currency_value').text((sub_total + tax_total).toFixed(2));
        },
        _onClickEditAddress: function(e) {
            var self = this;
            var $target = $(e.target);
            $target = $(e.target).hasClass('js_edit_address') ? $target : $target.parents('.js_edit_address');
            var partner_id = $target.data('id');
            var mode = $target.data('mode');
            this.displayLoading();
            this._rpc({
                route: '/ordering/address',
                params: {
                    partner_id: partner_id,
                    order_id: this.blanket_order,
                    mode: ['edit',mode]
                },
            }).then(function(result) {
                if (result['form']) {
                    $('.blanket_address_checkout .oe_cart').hide();
                    $('#blanket_address_information').html(result['form']);
                } else {
                    console.log(result);
                }
                $.unblockUI();
            });
        },
        _onClickBackAddress: function(e) {
            $('#blanket_address_information').html('');
            $('.blanket_address_checkout .oe_cart').show();
        },
        _onClickSubmitEditAddress: function(e) {
            var self = this;
            var $target = $(e.target);
            var $form = $target.parents('form#address-form-information');
            var submit_data = $form.serializeArray().reduce(function(obj, item) {
                obj[item.name] = item.value;
                return obj;
            }, {});
            submit_data['partner_id'] = $form.data('id');
            submit_data['submitted'] = true;
            submit_data['order_id'] = this.blanket_order;
            this.displayLoading();
            this._rpc({
                route: '/ordering/address',
                params: submit_data,
            }).then(function(result) {
                if (result['kanban']) {
                    $('.blanket_address_checkout .oe_cart').replaceWith(result['kanban']);
                    $('#blanket_address_information').html('');
                    if (result['billing_id'])
                        self.order_data['billing_address'] = result['billing_id'];
                    if (result['shipping_id'])
                        self.order_data['shipping_address'] = result['shipping_id'];
                    self.setDataLocal()
                } else {
                    console.log(result);
                }
                $.unblockUI();
            })
        },
        _onClickAddAddress: function(e) {
            this.displayLoading();
            this._rpc({
                route: '/ordering/address',
                params: {
                    partner_id: -1,
                    order_id: this.blanket_order
                },
            }).then(function(result) {
                if (result['form']) {
                    $('.blanket_address_checkout .oe_cart').hide();
                    $('#blanket_address_information').html(result['form']);
                } else {
                    console.log(result);
                }
                $.unblockUI();
            });
        },
        _onClickChangeShipping: function (ev) {
            // change card CSS
            var $old = $('.all_shipping').find('.card.border_primary');
            $old.find('.btn-ship').toggle();
            $old.addClass('js_change_shipping');
            $old.removeClass('border_primary');

            var $new = $(ev.currentTarget).parent('div.one_kanban').find('.card');
            $new.find('.btn-ship').toggle();
            $new.removeClass('js_change_shipping');
            $new.addClass('border_primary');

            // change local data
            var $target = $(ev.target);
            $target = $target.hasClass('one_kanban') ? $target : $target.parents('.one_kanban');
            var partner_id = $target.find('.js_edit_address').data('id');
            this.order_data['shipping_address'] = partner_id;
            this.setDataLocal();
        },
        _onClickCheckoutConfirm: function(e) {
            var self = this;
            this.displayLoading();
            this._rpc({
                route: '/ordering/payment',
                params: {
                    blanket_order: this.blanket_order,
                    shipping_address: this.order_data.shipping_address
                },
            }).then(function(result) {
                self._onClickNextStep();
                if (result['form'])
                    $('.blanket_payment').html(result['form'])
                $.unblockUI();
            });
        },
        _onClickOrderConfirm: function(e) {
            var self = this;
            this.displayLoading();
            this.order_data['acquirer_id'] = $('input[name="pm_id"]:checked').data('acquirer-id');
            this._rpc({
                route: '/ordering/confirm',
                params: {
                    blanket_order: this.blanket_order,
                    order_data: this.order_data,
                },
            }).then(function(result) {
                console.log(result);
                $('.wizard_checkout').remove();
                $('.blanket_order_select').remove();
                $('.blanket_address_checkout').remove();
                $('.blanket_payment').remove();
                $('.blanket_confirm').html(result);
                $('.enterprise_sale').addClass('blanket_confirm_page').removeClass('enterprise_sale_10').removeClass('enterprise_sale_20').removeClass('enterprise_sale_40');
                self.removeDataLocal();
                $.unblockUI();
            });
        }
    })

});
