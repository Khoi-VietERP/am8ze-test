odoo.define('alphabricks_customer_stock_report.products_listing', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var session = require('web.session');
    var QWeb = core.qweb;

    var ProductsListingMain = AbstractAction.extend({
        template: 'ProductsListingMain',
        events: {
            'click #filter_apply_button': 'update_with_filter',
            'click #pdf': 'print_pdf',
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
                    model: 'customer.stock.report',
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
                model: 'customer.stock.report',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                if (initial_render) {
                    self.$('.py-control-panel').html(QWeb.render('FilterProductsListing', {get_info: datas,}));
                    self.$el.find('#date_from').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('#date_to').datepicker({dateFormat: 'dd-mm-yy'});

                    self.$el.find('.partner-multiple').select2({
                        placeholder: 'Select Partner...',
                    });

                    self.$el.find('.user-multiple').select2({
                        placeholder: 'Select User...',
                    });

                    self.$el.find('.product-multiple').select2({
                        placeholder: 'Select Product...',
                    });

                    self.$el.find('.category-multiple').select2({
                        placeholder: 'Select Category Code...',
                    });
                }
                self.$('.py-data-container-orig').html(QWeb.render('ProductsListingMainList', {
                    get_info: datas,
                }));
                self.loader_enable_ui();
            });
        },

        print_pdf: function (e) {
            var self = this
            e.preventDefault();
            self._rpc({
                model: 'customer.stock.report',
                method: 'print_report',
                args: [[self.wizard_id]],
            }).then(function (action) {
                // action['context'] = {
                //     'active_model': 'customer.stock.report',
                //     'active_id': self.wizard_id,
                // }
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
        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = false;
            var output = {start_date: false, end_date: false, partner_ids: false};

            if ($("#date_from").val()) {
                var dateObject = $("#date_from").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.start_date = dateString;
            }
            if ($("#date_to").val()) {
                var dateObject = $("#date_to").datepicker("getDate");
                var dateString = $.datepicker.formatDate("yy-mm-dd", dateObject);
                output.end_date = dateString;
            }

            var partner_ids = [];
            var partner_list = $(".partner-multiple").select2('data')
            for (var i = 0; i < partner_list.length; i++) {
                partner_ids.push(parseInt(partner_list[i].id))
            }
            output.partner_ids = partner_ids

            var user_ids = [];
            var user_list = $(".user-multiple").select2('data')
            for (var i = 0; i < user_list.length; i++) {
                user_ids.push(parseInt(user_list[i].id))
            }
            output.user_ids = user_ids

            var product_ids = [];
            var product_list = $(".product-multiple").select2('data')
            for (var i = 0; i < product_list.length; i++) {
                product_ids.push(parseInt(product_list[i].id))
            }
            output.product_ids = product_ids

            var categ_ids = [];
            var category_list = $(".category-multiple").select2('data')
            for (var i = 0; i < category_list.length; i++) {
                categ_ids.push(parseInt(category_list[i].id))
            }
            output.categ_ids = categ_ids

            self._rpc({
                model: 'customer.stock.report',
                method: 'write',
                args: [self.wizard_id, output],
            }).then(function (res) {
                self.plot_data(self.initial_render);
            });
        },
    });

    core.action_registry.add('products.listing', ProductsListingMain);

    return {
        GstF5ReturnMain: ProductsListingMain,
    };
});
