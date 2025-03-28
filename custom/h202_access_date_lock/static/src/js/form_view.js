odoo.define('h202_access_date_lock.FormRenderer', function (require) {
    "use strict";

    var core = require('web.core');
    var config = require('web.config');
    var session = require('web.session');
    var pyUtils = require('web.py_utils');

    var FormRenderer = require('web.FormRenderer');

    FormRenderer.include({
        _renderView: function () {
            return this._super.apply(this, arguments).then(function () {
                if (this.state && this.state.data && this.state.data.check_date_lock) {
                    this.$el.addClass("lock_form_view");
                }
                else {
                    this.$el.removeClass('lock_form_view');
                }
            }.bind(this));
        },
    })
})