odoo.define('odoo_advance_search.ListController', function (require) {
"use strict";

var core = require('web.core');
var BasicController = require('web.BasicController');
var ListController = require('web.ListController');
var _t = core._t;

ListController.include({
	events: _.extend({}, ListController.prototype.events, {
    	'change thead .odoo_field_search_expan': '_change_odoo_field_search_expan',
    	'keydown thead .odoo_field_search_expan': '_onkeydownAdvanceSearch',
    }),
    _onkeydownAdvanceSearch: function (event) {
    	if (event.keyCode==13){
    		event.preventDefault();
        	event.stopPropagation();
        	this.trigger_up('search', this._controlPanel.getSearchQuery());
        	
    	}
    },
    _change_odoo_field_search_expan: function (event) {
    	event.preventDefault();
    	event.stopPropagation();
    	this.trigger_up('search', this._controlPanel.getSearchQuery());
    	
    },
	
});

});
