odoo.define('blanket_e_commerce.enterprise_sale', function (require) {
    'use strict';
    
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var VariantMixin = require('sale.VariantMixin');
    require("web.zoomodoo");
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

    publicWidget.registry.OrderingWebsiteSale = publicWidget.Widget.extend(VariantMixin, {
        selector: '.ordering_sale',
        read_events: {
            'change .js_quantity': '_onChangeOrderQuantity',
            'change .js_remark': '_onChangeOrderRemarks',
            'change .td-price': '_onChangePrice',
            'click .js_add_cart_json_button': '_onClickOrderQuantity',
            'click .next-steps': '_onClickNextStep',
            'click .prev-steps': '_onClickPrevStep',
            'click .address-checkout-confirm': '_onClickCheckoutConfirm',
            'click .address-checkout-back': '_onClickBackCart',
            'click .js_edit_address': '_onClickEditAddress',
            'click .address-form-back': '_onClickBackAddress',
            'click .address-form-submit': '_onClickSubmitEditAddress',
            'click .add-new-address': '_onClickAddAddress',
            'click .js_change_shipping': '_onClickChangeShipping',
            'click .payment-back': '_onClickWizardStep20',
            'click .blanket-order-confirm': '_onClickOrderConfirm',
            'click .product-gift-confirm': '_onClickProductGiftConfirm',
            'click .product-gift-back': '_onClickProductGiftBack',
            'click .floting_btn_cl_main': 'show_cart_toggle_views',
            'keyup .oe_search_box': '_onOrderFilter',
        },
        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);
            this.removeDataLocal()
            this.step = 10;
            this.popupShow = false
            this._setSteps();
            this.blanket_order = parseInt(getUrlParameter('blanket_order')) || 0;
            this.blanket_order_local = 'blanket_order_' + this.blanket_order;
            this.order_data = JSON.parse(localStorage.getItem(this.blanket_order_local) || '{}');
            this._setData();
            this._onClickPrevStep();
            return def;
        },
        show_cart_toggle_views: function(v){
            if (!this.popupShow) {
                $('#popup_toggle_summary_div').empty();
                $('#cart_products_summary').clone().appendTo('#popup_toggle_summary_div');
                $('#cart_total').clone().appendTo('#popup_toggle_summary_div');
                $('#cart_button').clone().appendTo('#popup_toggle_summary_div');
                $(".blanket_order_select").addClass("disabledpointer");
                window.scrollTo(0, 0)
                document.body.classList.add("disabledoverflow");
                this.popupShow = true
            }
            else {
                $('#popup_toggle_summary_div').empty();
                $(".blanket_order_select").removeClass("disabledpointer");
                document.body.classList.remove("disabledoverflow");
                this.popupShow = false
            }
            var popup = document.getElementById("myPopup");
            popup.classList.toggle("show");
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
            // remove old data structure
            if (this.order_data['order_line'].length > 0) {
                var _item = this.order_data['order_line'][Object.keys(this.order_data['order_line'])[0]]
                if (!_.isObject(_item)) this.order_data['order_line'] = {};
                this.removeDataLocal();
            }
            // load data from local
            // set order line
            _.each(this.order_data['order_line'], function(val, key) {
                var $input = $('input[data-line-id='+ key +']');
                $input.val(val['qty']);
                $input.trigger("change");
            });
            this.setDataLocal();
            this.updateCartSummaryPrice();
        },
        _onClickNextStep: function(e) {
            var self = this;
            console.log('_onClickNextStep')
            if (this.step == 10) {
                $('.search-query').hide();
                $('#cart_products_summary').hide();
                $('#cart_products').hide();
                $('#cart_lines_checkout').show();
                $('#mobile_button_confirm').show();
                $('.prev-steps').show();
                $('#po_number_form').show();
                $('#remarks_form').show();
                $('.next-steps').text('Confirm').show();
                this.step = 20;
                self.updateCartSummaryPrice()
                if (this.popupShow) {
                    $('.floting_btn_cl_main').trigger("click");
                }
            } else if (this.step == 20) {
                this.displayLoading();
                this._rpc({
                    route: '/ordering/confirm',
                    params: {
                        order: this.order_data,
                        po_number: $('#po_number').val(),
                        remarks: $('#input_remarks').val(),
                    },
                }).then(function(result) {
                    $('#product-gift-form').attr('action', result.url)
                    document.getElementById("product-gift-form").submit();
                    self.removeDataLocal()
                });
            }
        },
        _onClickPrevStep: function(e) {
            var self = this;
            $('.search-query').show();
            $('#cart_products_summary').show();
            $('#cart_products').show();
            $('#cart_lines_checkout').hide();
            $('#mobile_button_confirm').hide();
            $('#table_gift').html('');
            $('.prev-steps').hide();
            $('#po_number_form').hide();
            $('#remarks_form').hide();
            $('.next-steps').text('Process Checkout').show();
            this.step = 10;
            window.scrollTo(0, 0)
            this.updateCartSummaryPrice();
            if (this.popupShow) {
                $('.floting_btn_cl_main').trigger("click");
            }
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
            var $cartLinecheckout = $('#cart_lines_checkout').find('tr[data-line-id='+ lineId +']');
            var current_value = $target.val() && parseInt($target.val()) || 0
            var self = this;

            this._rpc({
                model: 'product.product',
                method: 'check_qty_available',
                args: [lineId, current_value],
            })
            .then(function (result) {
                current_value = result > 0 ? result : 0;
                $target.val(current_value);
                //update Cart Summary
                var line_is_hide = parseInt($cartLinecheckout.find('.td-qty input').val()) < 1 ? true : false;
                $cartLine.find('.td-qty').text(current_value);
                $cartLinecheckout.find('.td-qty input').val(current_value);
                //move line to top
                if (line_is_hide) {
                    $cartLine.prependTo($cartLine.parent('tbody'));
                    $cartLinecheckout.prependTo($cartLinecheckout.parent('tbody'));
                }
                //set default data
                if (!self.order_data['order_line'][lineId])
                    self.order_data['order_line'][lineId] = {'qty': 0, 'remarks': ''}
                // save data
                self.order_data['order_line'][lineId]['qty'] = current_value;
                // update data to local
                self.setDataLocal();
                self.updateCartSummaryPrice();
            })
        },
        _onChangeOrderRemarks: function(e) {
            var $target = $(e.target);
            var lineId = $target.data('line-id');
            //set default data
            if (!this.order_data['order_line'][lineId])
                this.order_data['order_line'][lineId] = {'qty': 0, 'remarks': ''}
            this.order_data['order_line'][lineId]['remarks'] = $target.val();
            this.setDataLocal();
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
        _onChangePrice: function (e) {
            var $cartProductsSummary = $('#cart_products_summary');
            var lines = $cartProductsSummary.find('tbody tr');
            var sub_total = 0.0;
            var tax_total = 0.0;

            _.each(lines, function(line) {
                if (!$(line).data('gift-line')) {
                    var $cartProductsCheckouts = $('#cart_lines_checkout tbody');
                    var $cartProductsCheckoutsLine = $cartProductsCheckouts.find("tr[data-line-id='"+ $(line).data('line-id') +"']");

                    var $line = $(line);
                    var sub_price = parseFloat($line.find('.td-price .oe_currency_value').text())
                    var tax_price = sub_price * $(line).data('line-tax');
                    sub_total += sub_price;
                    tax_total += tax_price;
                }
            })

            var amount_total = Math.round((sub_total + tax_total)*20)/20
            $cartProductsSummary.parent().parent().find('.amount_subtotal .oe_currency_value').text(sub_total.toFixed(2));
            $cartProductsSummary.parent().parent().find('.amount_tax .oe_currency_value').text(tax_total.toFixed(2));
            $cartProductsSummary.parent().parent().find('.amount_total .oe_currency_value').text(amount_total.toFixed(2));
        },
        updateCartSummaryPrice: function() {
            var $cartProductsSummary = $('#cart_products_summary');
            var lines = $cartProductsSummary.find('tbody tr');
            var $cartProductsCheckouts = $('#cart_lines_checkout tbody');
            var $cartProductsSummaryBody = $('#cart_products_summary tbody');
            var sub_total = 0.0;
            var tax_total = 0.0;
            var line_infor = {};
            var order_data = []
            var pricelist_id = false
            var self = this;
            var number_qty = 0
            var count_for_lines = 0
            _.each(lines, function(line) {
                count_for_lines += 1
                if (!$(line).data('gift-line')) {
                    if (!line_infor[$(line).data('line-id')])
                        line_infor[$(line).data('line-id')] = {
                            line_price_unit: $(line).data('line-price_unit'),
                            line_tax: $(line).data('line-tax') || 0,
                            total: 0.0
                        }
                    var _qty = parseInt($(line).find('.td-qty').text());
                    if (_qty > 0) {
                        order_data.push({
                            product : $(line).data('line-id'),
                            qty : _qty,
                        })
                        number_qty += 1
                    }
                    //calculate line price
                    var sub_price = _qty * line_infor[$(line).data('line-id')].line_price_unit;
                    var tax_price = sub_price * line_infor[$(line).data('line-id')].line_tax;
                    var $line = $(line);
                    // update show hide CheckoutsLine
                    var $cartProductsCheckoutsLine = $cartProductsCheckouts.find("tr[data-line-id='"+ $(line).data('line-id') +"']");
                    if (_qty > 0) {
                        $line.show()
                        $cartProductsCheckoutsLine.show()
                    } else {
                        $line.hide()
                        $cartProductsCheckoutsLine.hide()
                    };

                    var product_tmp_id = $(line).data('product-tmpl-id');
                    pricelist_id = $(line).data('pricelist-id');

                    if (product_tmp_id && _qty > 0) {
                         self._rpc({
                            model: 'sale.order',
                            method: 'get_pricelist_subtotal',
                            args: [product_tmp_id, _qty, pricelist_id],
                        })
                        .then(function (result) {
                            $line.find('.td-price .oe_currency_value').text((result * _qty).toFixed(2));
                            $line.find('.td-price .oe_currency_value').trigger("change")
                            $cartProductsCheckoutsLine.find('.td-price .oe_currency_value').text((result * _qty).toFixed(2));
                        })
                    }
                    else {
                        $line.find('.td-price .oe_currency_value').text(sub_price.toFixed(2));
                        // $line.find('.td-price .oe_currency_value').trigger("change")
                        $cartProductsCheckoutsLine.find('.td-price .oe_currency_value').text(sub_price.toFixed(2));
                    }

                    sub_total += sub_price;
                    tax_total += tax_price;
                }
                else {
                    $(line).remove()
                }
                if (count_for_lines == lines.length) {
                    self._onChangePrice()
                }
            });

            $('#number_product_cart').text(number_qty)

            if (self.step == 20) {
                this._rpc({
                    route: '/ordering/get_gift',
                    params: {
                        pricelist_id: pricelist_id,
                        order_data: order_data,
                        step : 20,
                    },
                }).then(function(result) {
                    if (result) {
                        $('#table_gift').html(result);
                    }
                    $.unblockUI();
                });
            }
            if (self.step == 10) {
                this._rpc({
                    route: '/ordering/get_gift',
                    params: {
                        pricelist_id: pricelist_id,
                        order_data: order_data,
                        step : 10,
                    },
                }).then(function(result) {
                    _.each(result, function(gift_line) {
                        var $lineCartProductsSummary = $cartProductsSummaryBody.find("tr[data-line-id='"+ gift_line['product_id'] +"']");
                        var $lineGiftProductsSummary = $cartProductsSummaryBody.find("tr[data-line-id='"+ gift_line['product_id'] +"-gift']");

                        if ($lineGiftProductsSummary.length == 0) {
                            $lineCartProductsSummary.after(gift_line['template_gift_line'])
                        }
                    })
                    $.unblockUI();
                });
            }
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
                var url = result.url
                $('.blanket_confirm').html(url);
                $('.enterprise_sale').addClass('blanket_confirm_page').removeClass('enterprise_sale_10').removeClass('enterprise_sale_20').removeClass('enterprise_sale_40');
                if (!result.has_rule) {
                    self.removeDataLocal();
                }

                $.unblockUI();
            });
        }
    })

});
