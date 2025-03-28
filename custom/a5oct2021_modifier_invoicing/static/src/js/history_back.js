odoo.define('a5oct2021_modifier_invoicing.history_back', function (require) {
"use strict";

    var core = require('web.core');
    var _t = core._t;

    function HistoryBack(parent, action) {
        window.history.back()
    }

    core.action_registry.add("history_back", HistoryBack);

});