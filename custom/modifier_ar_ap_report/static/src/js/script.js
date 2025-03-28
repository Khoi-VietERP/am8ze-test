odoo.define('modifier_ar_ap_report.dynamic_reports', function (require) {
    "use strict";

    var core = require('web.core');
    var DynamicTbMain = require('account_dynamic_reports.DynamicTbMain');
    var field_utils = require('web.field_utils');
    var QWeb = core.qweb;

    var _t = core._t;

    DynamicTbMain.DynamicPaMain.include({
        plot_data: function (initial_render = true) {
            var self = this;
            self.loader_disable_ui();
            var node = self.$('.py-data-container-orig');
            var last;
            while (last = node.lastChild) node.removeChild(last);
            self._rpc({
                model: 'ins.partner.ageing',
                method: 'get_report_datas',
                args: [[self.wizard_id]],
            }).then(function (datas) {
                self.filter_data = datas[0]
                self.ageing_data = datas[1]
                self.period_dict = datas[2]
                self.period_list = datas[3]
                self.partner_ids = datas[4]
                _.each(self.ageing_data, function (k, v) {
                    var formatOptions = {
                        currency_id: k.company_currency_id,
                        noSymbol: true,
                    };
                    for (var z = 0; z < self.period_list.length; z++) {
                        k[self.period_list[z]] = self.formatWithSign(k[self.period_list[z]], formatOptions, k[self.period_list[z]] < 0 ? '-' : '');
                    }
                    k.total = self.formatWithSign(k.total, formatOptions, k.total < 0 ? '-' : '');
                });
                if (initial_render) {
                    var titel = "Partner Ageing"
                    if (self._title) {
                        titel = self._title
                    }
                    var header = "<div style='text-align: center;border-top:1px solid #cccccc;margin-top: 10px'><p style='font-size: 30px'>"+self.filter_data['company_name']+"</p>" +
                    "<p style='font-size: 18px'><strong>"+titel+"</strong><br/><span>As on date: "+self.change_date_format(self.filter_data['as_on_date'])+"</span></p></div>"

                    self.$('.py-control-panel').html(QWeb.render('FilterSectionPa', {
                        filter_data: self.filter_data,
                    }) + header + QWeb.render('ButtonExpandPa'));
                    // self.$el.find('#as_on_date').datepicker({dateFormat: 'dd-mm-yy'});
                    self.$el.find('.type-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Account Type...',
                    });
                    self.$el.find('.partner-type-multiple').select2({
                        maximumSelectionSize: 1,
                        placeholder: 'Select Partner Type...',
                    });
                    self.$el.find('.partner-multiple').select2({
                        placeholder: 'Select Partner...',
                    });
                    self.$el.find('.partner-tag-multiple').select2({
                        placeholder: 'Select Tag...',
                    });
                    self.$el.find('.extra-multiple').select2({
                        placeholder: 'Extra Options...',
                    })
                        .val('include_details').trigger('change')
                    ;
                }

                self.$('.py-data-container-orig').html(QWeb.render('DataSectionPa', {
                    ageing_data: self.ageing_data,
                    period_dict: self.period_dict,
                    period_list: self.period_list,
                    partner_ids: self.filter_data['partner_ids'],
                }));
                self.$('.py-breadcrumb').html("<li>"+titel+"</li>");
                self.loader_enable_ui();
            });
        },
        // print_pdf: function (e) {
        //     var self = this;
        //     self._rpc({
        //         model: 'ins.partner.ageing',
        //         method: 'action_pdf',
        //         args: [[self.wizard_id]],
        //     }).then(function (action) {
        //         action.context.active_ids = [self.wizard_id];
        //         return self.do_action(action);
        //     });
        // },
        update_with_filter: function (event) {
            event.preventDefault();
            var self = this;
            self.initial_render = true;
            var output = {}
            // output.type = false;
            // output.include_details = false;
            // output.partner_type = false;
            // output.bucket_1 = $("#bucket_1").val();
            // output.bucket_2 = $("#bucket_2").val();
            // output.bucket_3 = $("#bucket_3").val();
            // output.bucket_4 = $("#bucket_4").val();
            // output.bucket_5 = $("#bucket_5").val();
            if ((parseInt(output.bucket_1) >= parseInt(output.bucket_2)) | (parseInt(output.bucket_2) >= parseInt(output.bucket_3)) |
                (parseInt(output.bucket_3) >= parseInt(output.bucket_4)) | (parseInt(output.bucket_4) >= parseInt(output.bucket_5))) {
                alert('Bucket order must be ascending');
                return;
            }
            if ($(".type-multiple").select2('data').length === 1) {
                output.type = $(".type-multiple").select2('data')[0].id
            }
            if ($(".partner-type-multiple").select2('data').length === 1) {
                output.partner_type = $(".partner-type-multiple").select2('data')[0].id
            }
            var partner_ids = [];
            var partner_list = $(".partner-multiple").select2('data')
            for (var i = 0; i < partner_list.length; i++) {
                partner_ids.push(parseInt(partner_list[i].id))
            }
            output.partner_ids = partner_ids
            var partner_tag_ids = [];
            var partner_tag_list = $(".partner-tag-multiple").select2('data')
            for (var i = 0; i < partner_tag_list.length; i++) {
                partner_tag_ids.push(parseInt(partner_tag_list[i].id))
            }
            output.partner_category_ids = partner_tag_ids
            if ($("#as_on_date").val()) {
                output['as_on_date'] = self.$el.find('#as_on_date').val();
            }
            var options_list = $(".extra-multiple").select2('data')
            for (var i = 0; i < options_list.length; i++) {
                if (options_list[i].id === 'include_details') {
                    output.include_details = true;
                }
                if (options_list[i].id === 'hide_line') {
                    output.hide_line = true;
                }
            }
            self._rpc({
                model: 'ins.partner.ageing',
                method: 'write',
                args: [self.wizard_id, output],
            }).then(function (res) {
                self.plot_data(self.initial_render);
            });
        },
    })

});