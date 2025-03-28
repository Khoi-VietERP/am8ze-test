odoo.define('odoo-debrand.crash_manager', function(require) {
"use strict";

var framework = require('web.framework');
var core = require('web.core');
var CrashManager = require('web.CrashManager').CrashManager;
var ErrorDialog = require('web.CrashManager').ErrorDialog;
var ErrorDialogRegistry = require('web.ErrorDialogRegistry');

var _t = core._t;
let active = true;

const isBrowserChrome = function () {
    return $.browser.chrome && // depends on jquery 1.x, removed in jquery 2 and above
        navigator.userAgent.toLocaleLowerCase().indexOf('edge') === -1; // as far as jquery is concerned, Edge is chrome
};

CrashManager.include({
    show_error: function (error) {
        console.log('show_error', error);
        if (!active) {
            return;
        }
        error.traceback = error.data.debug;
        var dialogClass = error.data.context && ErrorDialogRegistry.get(error.data.context.exception_class) || ErrorDialog;
        var dialog = new dialogClass(this, {
            title: _.str.capitalize(error.type) || _t("System Error"),
        }, error);


        // When the dialog opens, initialize the copy feature and destroy it when the dialog is closed
        var $clipboardBtn;
        var clipboard;
        if (window.location.href.indexOf('debug') !== -1) {
            dialog.opened(function () {
                // When the full traceback is shown, scroll it to the end (useful for better python error reporting)
                dialog.$(".o_error_detail").on("shown.bs.collapse", function (e) {
                    e.target.scrollTop = e.target.scrollHeight;
                });

                $clipboardBtn = dialog.$(".o_clipboard_button");
                $clipboardBtn.tooltip({title: _t("Copied !"), trigger: "manual", placement: "left"});
                clipboard = new window.ClipboardJS($clipboardBtn[0], {
                    text: function () {
                        return (_t("Error") + ":\n" + error.message + "\n\n" + error.data.debug).trim();
                    },
                    // Container added because of Bootstrap modal that give the focus to another element.
                    // We need to give to correct focus to ClipboardJS (see in ClipboardJS doc)
                    // https://github.com/zenorocha/clipboard.js/issues/155
                    container: dialog.el,
                });
                clipboard.on("success", function (e) {
                    _.defer(function () {
                        $clipboardBtn.tooltip("show");
                        _.delay(function () {
                            $clipboardBtn.tooltip("hide");
                        }, 800);
                    });
                });
            });
            dialog.on("closed", this, function () {
                $clipboardBtn.tooltip('dispose');
                clipboard.destroy();
            });
        } else {
            dialog.opened(function () {
                dialog.$el.html('');
            });
        }
        return dialog.open();
    },
    init: function () {
        var self = this;
        active = true;
        this.isConnected = true;

        this._super.apply(this, arguments);

        console.log('CrashManager init');

        // crash manager integration
        core.bus.off('rpc_error').on('rpc_error', this, this.rpc_error);
        window.onerror = function (message, file, line, col, error) {
            // Scripts injected in DOM (eg: google API's js files) won't return a clean error on window.onerror.
            // The browser will just give you a 'Script error.' as message and nothing else for security issue.
            // To enable onerror to work properly with CORS file, you should:
            //   1. add crossorigin="anonymous" to your <script> tag loading the file
            //   2. enabling 'Access-Control-Allow-Origin' on the server serving the file.
            // Since in some case it wont be possible to to this, this handle should have the possibility to be
            // handled by the script manipulating the injected file. For this, you will use window.onOriginError
            // If it is not handled, we should display something clearer than the common crash_manager error dialog
            // since it won't show anything except "Script error."
            // This link will probably explain it better: https://blog.sentry.io/2016/05/17/what-is-script-error.html
            if (!file && !line && !col) {
                // Chrome and Opera set "Script error." on the `message` and hide the `error`
                // Firefox handles the "Script error." directly. It sets the error thrown by the CORS file into `error`
                if (window.onOriginError) {
                    window.onOriginError();
                    delete window.onOriginError;
                } else {
                    self.show_error({
                        type: _t("Client Error"),
                        message: _t("Unknown CORS error"),
                        data: {debug: _t("An unknown CORS error occured. The error probably originates from a JavaScript file served from a different origin. (Opening your browser console might give you a hint on the error.)")},
                    });
                }
            } else {
                // ignore Chrome video internal error: https://crbug.com/809574
                if (!error && message === 'ResizeObserver loop limit exceeded') {
                    return;
                }
                var traceback = error ? error.stack : '';
                self.show_error({
                    type: _t("Client Error"),
                    message: message,
                    data: {debug: file + ':' + line + "\n" + _t('Traceback:') + "\n" + traceback},
                });
            }
        };

        // listen to unhandled rejected promises, and throw an error when the
        // promise has been rejected due to a crash
        core.bus.off('crash_manager_unhandledrejection').on('crash_manager_unhandledrejection', this, function (ev) {
            if (ev.reason && ev.reason instanceof Error) {
                // Error.prototype.stack is non-standard.
                // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error
                // However, most engines provide an implementation.
                // In particular, Chrome formats the contents of Error.stack
                // https://v8.dev/docs/stack-trace-api#compatibility
                let traceback;
                if (isBrowserChrome()) {
                    traceback = ev.reason.stack;
                } else {
                    traceback = `${_t("Error:")} ${ev.reason.message}\n${ev.reason.stack}`;
                }
                self.show_error({
                    type: _t("Client Error"),
                    message: '',
                    data: {debug: _t('Traceback:') + "\n" + traceback},
                });
            } else {
                // the rejection is not due to an Error, so prevent the browser
                // from displaying an 'unhandledrejection' error in the console
                ev.stopPropagation();
                ev.stopImmediatePropagation();
                ev.preventDefault();
            }
        });
    },
    show_message: function(exception) {
        return this.show_error({
            type: _t("Client Error"),
            message: exception,
            data: {debug: ""}
        });
    },
});

function logout() {
    framework.redirect('/web/session/logout');
    return new Promise(function() {});
}
core.action_registry.add("logout", logout);

});