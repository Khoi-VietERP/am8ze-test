odoo.define('inventory_forecast.FormView', function (require) {
"use strict";

var FormRenderer = require('web.FormRenderer');
var FieldOne2Many = require('web.relational_fields').FieldOne2Many;

FormRenderer.include({
    autofocus: function () {
        this._super.apply(this, arguments);
        var self = this;

        var last_month_list = []
        var current = new Date();

        current.setMonth(current.getMonth()-1);
        var previousMonth = current.toLocaleString('default', { month: 'short',year: '2-digit' });
        last_month_list.push(previousMonth)

        current.setMonth(current.getMonth()-1);
        var previousMonth = current.toLocaleString('default', { month: 'short',year: '2-digit' });
        last_month_list.push(previousMonth)

        current.setMonth(current.getMonth()-1);
        var previousMonth = current.toLocaleString('default', { month: 'short',year: '2-digit' });
        last_month_list.push(previousMonth)

        current.setMonth(current.getMonth()-1);
        var previousMonth = current.toLocaleString('default', { month: 'short',year: '2-digit' });
        last_month_list.push(previousMonth)

        current.setMonth(current.getMonth()-1);
        var previousMonth = current.toLocaleString('default', { month: 'short',year: '2-digit' });
        last_month_list.push(previousMonth)

        current.setMonth(current.getMonth()-1);
        var previousMonth = current.toLocaleString('default', { month: 'short',year: '2-digit' });
        last_month_list.push(previousMonth)

        var hearders = $('.inventory_forecast_table table thead tr th')
        for (var hearder in hearders) {
            hearder = hearders[hearder]
            if (hearder.innerText == 'last_month_1') {
                hearder.innerText = last_month_list[0]
            }
            if (hearder.innerText == 'last_month_2') {
                hearder.innerText = last_month_list[1]
            }
            if (hearder.innerText == 'last_month_3') {
                hearder.innerText = last_month_list[2]
            }
            if (hearder.innerText == 'last_month_4') {
                hearder.innerText = last_month_list[3]
            }
            if (hearder.innerText == 'last_month_5') {
                hearder.innerText = last_month_list[4]
            }
            if (hearder.innerText == 'last_month_6') {
                hearder.innerText = last_month_list[5]
            }
        }
    }
})

FieldOne2Many.include({
     reset: function (record, ev) {
        var self = this;

        var last_month_list = []
        var current = new Date();

        current.setMonth(current.getMonth()-1);
        var previousMonth = current.toLocaleString('default', { month: 'short',year: '2-digit' });
        last_month_list.push(previousMonth)

        current.setMonth(current.getMonth()-1);
        var previousMonth = current.toLocaleString('default', { month: 'short',year: '2-digit' });
        last_month_list.push(previousMonth)

        current.setMonth(current.getMonth()-1);
        var previousMonth = current.toLocaleString('default', { month: 'short',year: '2-digit' });
        last_month_list.push(previousMonth)

        current.setMonth(current.getMonth()-1);
        var previousMonth = current.toLocaleString('default', { month: 'short',year: '2-digit' });
        last_month_list.push(previousMonth)

        current.setMonth(current.getMonth()-1);
        var previousMonth = current.toLocaleString('default', { month: 'short',year: '2-digit' });
        last_month_list.push(previousMonth)

        current.setMonth(current.getMonth()-1);
        var previousMonth = current.toLocaleString('default', { month: 'short',year: '2-digit' });
        last_month_list.push(previousMonth)

        return this._super.apply(this, arguments).then(function () {
            var hearders = $('.inventory_forecast_table table thead tr th')
            for (var hearder in hearders) {
                hearder = hearders[hearder]
                if (hearder.innerText == 'last_month_1') {
                    hearder.innerText = last_month_list[0]
                }
                if (hearder.innerText == 'last_month_2') {
                    hearder.innerText = last_month_list[1]
                }
                if (hearder.innerText == 'last_month_3') {
                    hearder.innerText = last_month_list[2]
                }
                if (hearder.innerText == 'last_month_4') {
                    hearder.innerText = last_month_list[3]
                }
                if (hearder.innerText == 'last_month_5') {
                    hearder.innerText = last_month_list[4]
                }
                if (hearder.innerText == 'last_month_6') {
                    hearder.innerText = last_month_list[5]
                }
            }
        });
    },
})

});
