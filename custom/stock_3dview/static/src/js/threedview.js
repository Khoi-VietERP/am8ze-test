odoo.define('stock_3dview.3DView', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var AbstractController = require('web.AbstractController');
    var AbstractModel = require('stock_3dview.3DViewModel');
    var AbstractRenderer = require('stock_3dview.3DViewRenderer');
    var AbstractView = require('web.AbstractView');
    var data_manager = require('web.data_manager');
    var session = require('web.session');
    var view_registry = require('web.view_registry');
    var _lt = core._lt;
    var QWeb = core.qweb;

    if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

    var ThreeDView = AbstractView.extend({
        config: {
            Model: AbstractModel,
            Controller: AbstractController,
            Renderer: AbstractRenderer,
        },
        display_name: _lt('ThreeD View'),
        icon: 'fa-cubes',
        template: '3DView',
        view_type: 'threedview',

        init: function (parent, context) {
            this.context = context;
            this.withSearchPanel = false;
            this._super.apply(this, arguments);
            return this;
        },

    });

    view_registry.add('threedview', ThreeDView);

        return ThreeDView;
    });

