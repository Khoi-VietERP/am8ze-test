odoo.define('dragdrop_attachment.Attachment', function (require) {
    "use strict";

    var AttachmentBox = require('mail.AttachmentBox');
    var Sidebar = require('web.Sidebar');
    var Chatter = require('mail.Chatter');
    var core = require('web.core');

    var _t = core._t;
    var internal = {
        drag_and_drop_init: false,
        form_selector: '.o_chatter_button_attachment',
        model : false
    };

    Chatter.include({
        start: function () {
            var self = this
            this._super.apply(this, arguments);
            if (!this._disableAttachmentBox ) {
                if (internal.model !== this.context.default_model) {
                    internal.drag_and_drop_init = false
                }
                if (internal.drag_and_drop_init === true) {
                    return;
                }

                var main = document.querySelector('body > .o_action_manager');

                if (null === main) {
                    return;
                }
                internal.form_selector = internal.form_selector;

                var counter_drag_enter = 0;
                document.addEventListener('dragenter', function (event) {
                    event.preventDefault();
                    if (null === document.querySelector(internal.form_selector)) {
                        return;
                    }

                    counter_drag_enter++;
                    main.classList.add('dragover');
                    main.setAttribute('data-dragover-text', _t('Drop files here to add it'));
                }, false);
                document.addEventListener('dragleave', function (event) {
                    event.preventDefault();
                    if (null === document.querySelector(internal.form_selector)) {
                        return;
                    }

                    counter_drag_enter--;
                    if (0 === counter_drag_enter) {
                        main.classList.remove('dragover');
                    }
                }, false);

                main.addEventListener('dragover', function (event) {
                    event.stopPropagation();
                    event.preventDefault();
                    event.dataTransfer.dropEffect = 'copy';
                }, false);

                main.addEventListener('drop', function (event) {
                    event.stopPropagation();
                    event.preventDefault();

                    counter_drag_enter = 0;
                    main.classList.remove('dragover');

                    self.ondrop(event);
                }, false);

                internal.drag_and_drop_init = true;
            }
        },

        ondrop: function (event) {
            var form_upload = document.querySelector(internal.form_selector);
            var self = this
            if (null === form_upload) {
                return;
            }

            var form_data = new FormData();
            for (var iterator = 0, file; file = event.dataTransfer.files[iterator]; iterator++) {
                form_data.set('ufile', file);
                form_data.set('model', this.context.default_model);
                form_data.set('id', this.context.default_res_id);
                form_data.set('callback', _.uniqueId('oe_fileupload'));
                form_data.set('csrf_token', odoo.csrf_token);
                $.ajax({
                    url: '/web/binary/upload_attachment',
                    method: 'post',
                    type: 'post',
                    processData: false,
                    contentType: false,
                    data: form_data,
                    success: function (data) {
                        $('body').append(data);
                    },
                    error: function (jqXHR, textStatus, errorThrown) {
                        console.error(jqXHR, textStatus, errorThrown);
                    }
                }).then(function () {
                    self._reloadAttachmentBox();
                    self.trigger_up('reload');
                });
            }
        }
    })

    // AttachmentBox.include({
    //     start: function (parent) {
    //         var self = this;
    //         this._super.apply(this, arguments);
    //         if (internal.drag_and_drop_init === true) {
    //             return;
    //         }
    //
    //         var main = document.querySelector('body > .o_action_manager');
    //
    //         if (null === main) {
    //             return;
    //         }
    //         internal.form_selector = internal.form_selector;
    //
    //         var counter_drag_enter = 0;
    //         document.addEventListener('dragenter', function (event) {
    //             event.preventDefault();
    //             if (null === document.querySelector(internal.form_selector)) {
    //                 return;
    //             }
    //
    //             counter_drag_enter++;
    //             main.classList.add('dragover');
    //             main.setAttribute('data-dragover-text', _t('Drop files here to add it'));
    //         }, false);
    //         document.addEventListener('dragleave', function (event) {
    //             event.preventDefault();
    //             if (null === document.querySelector(internal.form_selector)) {
    //                 return;
    //             }
    //
    //             counter_drag_enter--;
    //             if (0 === counter_drag_enter) {
    //                 main.classList.remove('dragover');
    //             }
    //         }, false);
    //
    //         main.addEventListener('dragover', function (event) {
    //             event.stopPropagation();
    //             event.preventDefault();
    //             event.dataTransfer.dropEffect = 'copy';
    //         }, false);
    //
    //         main.addEventListener('drop', function (event) {
    //             event.stopPropagation();
    //             event.preventDefault();
    //
    //             counter_drag_enter = 0;
    //             main.classList.remove('dragover');
    //
    //             self.ondrop(event);
    //         }, false);
    //
    //         internal.drag_and_drop_init = true;
    //     },
    //     ondrop: function (event) {
    //         var form_upload = document.querySelector(internal.form_selector);
    //         debugger
    //         if (null === form_upload) {
    //             return;
    //         }
    //
    //         var form_data = new FormData();
    //         for (var iterator = 0, file; file = event.dataTransfer.files[iterator]; iterator++) {
    //             form_data.set('ufile', file);
    //             form_data.set('model', this.currentResModel);
    //             form_data.set('id', this.currentResID);
    //             form_data.set('callback', _.uniqueId('oe_fileupload'));
    //             form_data.set('csrf_token', odoo.csrf_token);
    //             $.ajax({
    //                 url: form_upload.getAttribute('action'),
    //                 method: form_upload.getAttribute('method'),
    //                 type: form_upload.getAttribute('method'),
    //                 processData: false,
    //                 contentType: false,
    //                 data: form_data,
    //                 success: function (data) {
    //                     $('body').append(data);
    //                 },
    //                 error: function (jqXHR, textStatus, errorThrown) {
    //                     console.error(jqXHR, textStatus, errorThrown);
    //                 }
    //             });
    //         }
    //     }
    // });

})