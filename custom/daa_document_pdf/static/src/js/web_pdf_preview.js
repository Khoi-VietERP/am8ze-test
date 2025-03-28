odoo.define('daa_document_pdf.preview', function (require) {
    'use strict';

    var core = require('web.core');
    // var ActionManager = require('web.ActionManager');
    var framework = require('web.framework');
    var utils = require('web.utils');
    //
    var FieldBinaryFile = require('web.basic_fields').FieldBinaryFile;
    var PreviewDialog = require('report_pdf_preview.PreviewDialog');

    var _t = core._t;

    FieldBinaryFile.include({
        on_save_as: function (ev) {
            var self = this;

            console.log('on_save_as 2', ev);
            if (!this.value) {
                this.do_warn(_t("Save As..."), _t("The field is empty, there's nothing to save !"));
                ev.stopPropagation();
            } else if (this.res_id) {
                var filename_fieldname = this.attrs.filename;
                var filename = this.recordData[filename_fieldname] || "";
                if (filename && filename.split('.').pop().toLowerCase() === 'pdf') {
                    var queryObj = {
                        model: this.model,
                        field: this.name,
                        id: this.res_id,
                    };
                    var queryString = $.param(queryObj);
                    var fileURI = '/web/content?' + queryString;

                    var dialog = PreviewDialog.createPreviewDialog(self, fileURI, false, "pdf", filename);
                    $.when(dialog, dialog._opened).then(function (dialog) {
                        var a = 1;
                        dialog.$modal.find('.preview-download').hide();

                    })
                    framework.unblockUI();
                } else {
                    return self._super(ev);
                }
            }
        },
    });
    //
    // ActionManager.include({
    //     _executeReportAction: function (action, options) {
    //         var self = this;
    //         action = _.clone(action);
    //
    //         if (action.report_type === 'qweb-pdf') {
    //             return this.call('report', 'checkWkhtmltopdf').then(function (state) {
    //                 var active_ids_path = '/' + action.context.active_ids.join(',');
    //                 // var url = '/report/pdf/' + action.report_name + active_ids_path;
    //                 var url = self._makeReportUrls(action)['pdf'];
    //                 var filename = action.report_name;
    //                 var title = action.display_name;
    //                 var def = $.Deferred()
    //                 var dialog = PreviewDialog.createPreviewDialog(self, url, false, "pdf", title);
    //                 $.when(dialog, dialog._opened).then(function (dialog) {
    //                     var a = 1;
    //                     dialog.$modal.find('.preview-download').hide();
    //
    //                 })
    //                 framework.unblockUI();
    //             });
    //
    //         } else {
    //             return self._super(action, options);
    //         }
    //
    //     }
    // });

});