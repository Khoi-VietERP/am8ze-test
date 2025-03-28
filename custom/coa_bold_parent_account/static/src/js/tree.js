odoo.define('mypet.bold', function (require) {
    "use strict";

    var fields = require('web.basic_fields');
    var registry = require('web.field_registry');

    var BoldWidget = fields.FieldChar.extend({
        _renderReadonly: function () {
            this._super();
            if (this.recordData && this.recordData.internal_type == 'view') {
                var old_html_render = this.$el.html();
                var new_html_render = '<b>' + old_html_render + '</b>'
                this.$el.html(new_html_render);
            }
        },
    });

    registry.add('bold_widget', BoldWidget);
});