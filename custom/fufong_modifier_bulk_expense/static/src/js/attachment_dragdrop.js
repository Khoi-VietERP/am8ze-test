//-*- coding: utf-8 -*-
odoo.define('fufong_modifier_bulk_expense.attachment_dragdrop', function (require) {
    "use strict";
    var Sidebar = require('web.Sidebar');
    var core = require('web.core');
    var FormController = require('web.FormController');

    var _t = core._t;
    var internal = {
        drag_and_drop_init: false,
        form_selector: '.bulk_form_view',
    };

    FormController.include({
        init: function () {
            var self = this;
            this._super.apply(this, arguments);
            if (internal.drag_and_drop_init === true) {
                return;
            }

            var main = document.querySelector('body > .o_action_manager');
            internal.form_selector = internal.form_selector;
            var model = this.modelName
            var record_id = this.initialState.data.id

            if (null === main || model !== 'bulk.expense' || !record_id) {
                return;
            }
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
                if (null === document.querySelector(internal.form_selector)) {
                    return;
                }
                event.stopPropagation();
                event.preventDefault();

                counter_drag_enter = 0;
                main.classList.remove('dragover');
                self.ondrop(event, record_id);

            }, false);

            internal.drag_and_drop_init = true;
        },
        ondrop: function (event, record_id) {
            var items_len = event.dataTransfer.items.length
            for (var iterator = 0, file; file = event.dataTransfer.items[iterator]; iterator++) {
                var form = new FormData();
                form.append('ufile', file.getAsFile());
                form.append('record', record_id);
                form.append('csrf_token', core.csrf_token);
                $.ajax({
                    data: form,
                    type: 'POST',
                    dataType: 'json',
                    url: '/bulk_expense/attachment/add',
                    enctype: 'multipart/form-data',
                    processData: false,
                    contentType: false
                }).fail(function (jqXHR, textStatus) {
                    console.error(textStatus);
                }).then(function () {
                    if (iterator === items_len) {
                        window.location.reload()
                    }
                })
            }
        },
    });
})
