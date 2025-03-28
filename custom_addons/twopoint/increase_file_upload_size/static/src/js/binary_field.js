odoo.define('increase_file_upload_size.basic_fields', function (require) {
    "use strict";

    var BasicFields = require('web.basic_fields');
    var AbstractFieldBinary = BasicFields.AbstractFieldBinary

    AbstractFieldBinary.include({
        init: function (parent, name, record) {
            this._super.apply(this, arguments);
            this.max_upload_size = 150 * 1024 * 1024; // 25Mo
        },
    })
})