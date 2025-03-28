odoo.define('daa_contact_modifier.ParterFormView', function (require) {
"use strict";

    var Chatter = require('mail.Chatter')
    var config = require('web.config');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    Chatter.include({
        _renderButtons: function () {

            if (this.record && this.record.context && this.record.context.default_is_debtor == true) {
                return QWeb.render('mail.chatter.Buttons', {
                    logNoteButton: this.hasLogButton,
                    isMobile: config.device.isMobile,
                });
            }
            else {
                return this._super.apply(this, arguments);
            }
        },
    })
});
