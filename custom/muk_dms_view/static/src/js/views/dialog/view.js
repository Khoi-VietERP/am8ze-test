/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Documents View 
*    (see https://mukit.at).
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Lesser General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Lesser General Public License for more details.
*
*    You should have received a copy of the GNU Lesser General Public License
*    along with this program. If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define('muk_dms_view.DocumentTreeDialogView', function(require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var config = require('web.config');
var session = require('web.session');
var web_client = require('web.web_client');

var Widget = require('web.Widget');
var Dialog = require('web.Dialog');

var DocumentsModel = require('muk_dms_view.DocumentsModel');
var DocumentsRenderer = require('muk_dms_view.DocumentsRenderer');
var DocumentsDialogController = require('muk_dms_view.DocumentsDialogController');

var _t = core._t;
var QWeb = core.qweb;

var DocumentTreeDialogView = Widget.extend({
	template: 'muk_dms.DocumentDialog',
	init: function(parent, params) {
		this._super.apply(this, arguments);
        this.controller = new DocumentsDialogController(this,
        	DocumentsModel, DocumentsRenderer,
        	_.extend({}, {
	        	dnd: false,
	        	contextmenu: true,
        	}, params));
    },
    start: function () {
        return $.when(this._super.apply(this, arguments))
	        .then(this._update_cp.bind(this))
	     	.then(this._update_view.bind(this));
    },
    _update_cp: function() {
    	this.$('#mk_searchview_input').keyup(this._trigger_search.bind(this));
    },
    _update_view: function() {
    	this.controller.appendTo(this.$('.mk_treeview'));
    },
    _trigger_search: _.debounce(function() {
		var val = this.$('#mk_searchview_input').val();
    	this.controller.search(val);
    }, 200),
});

return DocumentTreeDialogView;

});