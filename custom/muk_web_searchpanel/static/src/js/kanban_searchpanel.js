/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Search Panel 
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

odoo.define('muk_web_searchpanel.SearchPanel', function (require) {
"use strict";

var core = require('web.core');
var config = require('web.config');
var Domain = require('web.Domain');
var Widget = require('web.Widget');

var qweb = core.qweb;

var SearchPanel = Widget.extend({
    className: 'o_search_panel',
    events: {
        'click .o_search_panel_category_value header': '_onCategoryValueClicked',
        'click .o_search_panel_category_value .o_toggle_fold': '_onToggleFoldCategory',
        'click .o_search_panel_filter_group .o_toggle_fold': '_onToggleFoldFilterGroup',
        'change .o_search_panel_filter_value > div > input': '_onFilterValueChanged',
        'change .o_search_panel_filter_group > div > input': '_onFilterGroupChanged',
    },

    /**
     * @override
     * @param {Object} params
     * @param {Object} [params.defaultCategoryValues={}] the category value to
     *   activate by default, for each category
     * @param {Object} params.fields
     * @param {string} params.model
     * @param {Object} params.sections
     * @param {Array[]} params.searchDomain domain coming from controlPanel
     */
    init: function (parent, params) {
        this._super.apply(this, arguments);

        this.categories = _.pick(params.sections, function (section) {
            return section.type === 'category';
        });
        this.filters = _.pick(params.sections, function (section) {
            return section.type === 'filter';
        });

        this.defaultCategoryValues = params.defaultCategoryValues || {};
        this.fields = params.fields;
        this.model = params.model;
        this.searchDomain = params.searchDomain;
        
        this.loadProm = $.Deferred();
        this.loadPromLazy = true;
    },
    willStart: function () {
        var self = this;
        var loading = $.Deferred();
        var loadPromTimer = setTimeout(function () {
        	if(loading.state() !== 'resolved') {
        		loading.resolve();
        	}
        }, this.loadPromMaxTime || 1000);
        this._fetchCategories().then(function () {
            self._fetchFilters().then(function () {
            	if(loading.state() !== 'resolved') {
                	clearTimeout(loadPromTimer);
                	self.loadPromLazy = false;
                	loading.resolve();
            	}
            	self.loadProm.resolve();
            });
        });
        return $.when(loading, this._super.apply(this, arguments));
    },
    start: function () {
        var self = this;
        if(this.loadProm.state() !== 'resolved') {
        	this.$el.html($("<div/>", {
        		'class': "o_search_panel_loading",
        		'html': "<i class='fa fa-spinner fa-pulse' />"
        	}));
    	}
        this.loadProm.then(function() {
    		self._render();
    	});
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {Array[]} the current searchPanel domain based on active
     *   categories and checked filters
     */
    getDomain: function () {
        return this._getCategoryDomain().concat(this._getFilterDomain());
    },
    /**
     * Reload the filters and re-render. Note that we only reload the filters if
     * the controlPanel domain or searchPanel domain has changed.
     *
     * @param {Object} params
     * @param {Array[]} params.searchDomain domain coming from controlPanel
     * @returns {$.Promise}
     */
    update: function (params) {
        if(this.loadProm.state() === 'resolved') {
        	var newSearchDomainStr = JSON.stringify(params.searchDomain);
            var currentSearchDomainStr = JSON.stringify(this.searchDomain);
            if (this.needReload || (currentSearchDomainStr !== newSearchDomainStr)) {
                this.needReload = false;
                this.searchDomain = params.searchDomain;
                this._fetchFilters().then(this._render.bind(this));
            } else {
                this._render();
            }
        }
        return $.when();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {string} categoryId
     * @param {Object[]} values
     */
    _createCategoryTree: function (categoryId, values) {
        var category = this.categories[categoryId];
        var parentField = category.parentField;

        category.values = {};
        values.forEach(function (value) {
            category.values[value.id] = _.extend({}, value, {
                childrenIds: [],
                folded: true,
                parentId: value[parentField] && value[parentField][0] || false,
            });
        });
        Object.keys(category.values).forEach(function (valueId) {
            var value = category.values[valueId];
            if (value.parentId && category.values[value.parentId]) {
                category.values[value.parentId].childrenIds.push(value.id);
            } else {
            	value.parentId = false;
            	value[parentField] = false;
            }
        });
        category.rootIds = Object.keys(category.values).filter(function (valueId) {
            var value = category.values[valueId];
            return value.parentId === false;
        });
        category.activeValueId = false;
        
        if(!this.loadPromLazy) {
	        // set active value
	        var validValues = _.pluck(category.values, 'id').concat([false]);
	        // set active value from context
	        var value = this.defaultCategoryValues[category.fieldName];
	        // if not set in context, or set to an unknown value, set active value
	        // from localStorage
	        if (!_.contains(validValues, value)) {
	            var storageKey = this._getLocalStorageKey(category);
	            value = this.call('local_storage', 'getItem', storageKey);
	        }
	        
	        // if not set in localStorage either, select 'All'
	        category.activeValueId = _.contains(validValues, value) ? value : false;
	        
	        // unfold ancestor values of active value to make it is visible
	        if (category.activeValueId) {
	            var parentValueIds = this._getAncestorValueIds(category, category.activeValueId);
	            parentValueIds.forEach(function (parentValue) {
	                category.values[parentValue].folded = false;
	            });
	        }
        }
    },
    /**
     * @private
     * @param {string} filterId
     * @param {Object[]} values
     */
    _createFilterTree: function (filterId, values) {
        var filter = this.filters[filterId];

        // restore checked property
        values.forEach(function (value) {
            var oldValue = filter.values && filter.values[value.id];
            value.checked = oldValue && oldValue.checked || false;
        });

        filter.values = {};
        var groupIds = [];
        if (filter.groupBy) {
            var groups = {};
            values.forEach(function (value) {
                var groupId = value.group_id;
                if (!groups[groupId]) {
                    if (groupId) {
                        groupIds.push(groupId);
                    }
                    groups[groupId] = {
                        folded: false,
                        id: groupId,
                        name: value.group_name,
                        values: {},
                        tooltip: value.group_tooltip,
                        sequence: value.group_sequence,
                        sortedValueIds: [],
                    };
                    // restore former checked and folded state
                    var oldGroup = filter.groups && filter.groups[groupId];
                    groups[groupId].state = oldGroup && oldGroup.state || false;
                    groups[groupId].folded = oldGroup && oldGroup.folded || false;
                }
                groups[groupId].values[value.id] = value;
                groups[groupId].sortedValueIds.push(value.id);
            });
            filter.groups = groups;
            filter.sortedGroupIds = _.sortBy(groupIds, function (groupId) {
                return groups[groupId].sequence || groups[groupId].name;
            });
            Object.keys(filter.groups).forEach(function (groupId) {
                filter.values = _.extend(filter.values, filter.groups[groupId].values);
            });
        } else {
            values.forEach(function (value) {
                filter.values[value.id] = value;
            });
            filter.sortedValueIds = values.map(function (value) {
                return value.id;
            });
        }
    },
    /**
     * Fetch values for each category. This is done only once, at startup.
     *
     * @private
     * @returns {$.Promise} resolved when all categories have been fetched
     */
    _fetchCategories: function () {
        var self = this;
        var defs = Object.keys(this.categories).map(function (categoryId) {
            var category = self.categories[categoryId];
            var field = self.fields[category.fieldName];
            var def;
            if (field.type === 'selection') {
                var values = field.selection.map(function (value) {
                    return {id: value[0], display_name: value[1]};
                });
                def = $.when(values);
            } else {
                var categoryDomain = self._getCategoryDomain();
                var filterDomain = self._getFilterDomain();
                def = self._rpc({
                    method: 'search_panel_select_range',
                    model: self.model,
                    args: [category.fieldName],
                    kwargs: {
                        category_domain: categoryDomain,
                        filter_domain: filterDomain,
                        search_domain: self.searchDomain,
                    },
                }, {
                	shadow: true,
                }).then(function (result) {
                    category.parentField = result.parent_field;
                    return result.values;
                });
            }
            return def.then(function (values) {
                self._createCategoryTree(categoryId, values);
            });
        });
        return $.when.apply($, defs);
    },
    /**
     * Fetch values for each filter. This is done at startup, and at each reload
     * (when the controlPanel or searchPanel domain changes).
     *
     * @private
     * @returns {$.Promise} resolved when all filters have been fetched
     */
    _fetchFilters: function () {
        var self = this;
        var evalContext = {};
        Object.keys(this.categories).forEach(function (categoryId) {
            var category = self.categories[categoryId];
            evalContext[category.fieldName] = category.activeValueId;
        });
        var categoryDomain = this._getCategoryDomain();
        var filterDomain = this._getFilterDomain();
        var defs = Object.keys(this.filters).map(function (filterId) {
            var filter = self.filters[filterId];
            return self._rpc({
                method: 'search_panel_select_multi_range',
                model: self.model,
                args: [filter.fieldName],
                kwargs: {
                    category_domain: categoryDomain,
                    comodel_domain: Domain.prototype.stringToArray(filter.domain, evalContext),
                    disable_counters: filter.disableCounters,
                    filter_domain: filterDomain,
                    group_by: filter.groupBy || false,
                    search_domain: self.searchDomain,
                },
            }, {
            	shadow: true,
            }).then(function (values) {
                self._createFilterTree(filterId, values);
            });
        });
        return $.when.apply($, defs);
    },
    /**
     * Compute and return the domain based on the current active categories.
     *
     * @private
     * @returns {Array[]}
     */
    _getCategoryDomain: function () {
        var self = this;
        function categoryToDomain(domain, categoryId) {
            var category = self.categories[categoryId];
            if (category.activeValueId) {
                domain.push([category.fieldName, '=', category.activeValueId]);
            } else if(self.loadPromLazy && self.loadProm.state() !== 'resolved') {
            	var value = self.defaultCategoryValues[category.fieldName];
            	if (value) {
            		domain.push([category.fieldName, '=', value]);
            	}
            }
            return domain;
        }
        return Object.keys(this.categories).reduce(categoryToDomain, []);
    },
    /**
     * Compute and return the domain based on the current checked filters.
     * The values of a single filter are combined using a simple rule: checked values within
     * a same group are combined with an 'OR' (this is expressed as single condition using a list)
     * and groups are combined with an 'AND' (expressed by concatenation of conditions).
     * If a filter has no groups, its checked values are implicitely considered as forming
     * a group (and grouped using an 'OR').
     *
     * @private
     * @returns {Array[]}
     */
    _getFilterDomain: function () {
        var self = this;
        function getCheckedValueIds(values) {
            return Object.keys(values).reduce(function (checkedValues, valueId) {
                if (values[valueId].checked) {
                    checkedValues.push(values[valueId].id);
                }
                return checkedValues;
            }, []);
        }
        function filterToDomain(domain, filterId) {
            var filter = self.filters[filterId];
            if (filter.groups) {
                Object.keys(filter.groups).forEach(function (groupId) {
                    var group = filter.groups[groupId];
                    var checkedValues = getCheckedValueIds(group.values);
                    if (checkedValues.length) {
                        domain.push([filter.fieldName, 'in', checkedValues]);
                    }
                });
            } else if (filter.values) {
                var checkedValues = getCheckedValueIds(filter.values);
                if (checkedValues.length) {
                    domain.push([filter.fieldName, 'in', checkedValues]);
                }
            }
            return domain;
        }
        return Object.keys(this.filters).reduce(filterToDomain, []);
    },
    /**
     * The active id of each category is stored in the localStorage, s.t. it
     * can be restored afterwards (when the action is reloaded, for instance).
     * This function returns the key in the sessionStorage for a given category.
     *
     * @param {Object} category
     * @returns {string}
     */
    _getLocalStorageKey: function (category) {
        return 'searchpanel_' + this.model + '_' + category.fieldName;
    },
    /**
     * @private
     * @param {Object} category
     * @param {integer} categoryValueId
     * @returns {integer[]} list of ids of the ancestors of the given value in
     *   the given category
     */
    _getAncestorValueIds: function (category, categoryValueId) {
        var categoryValue = category.values[categoryValueId];
        var parentId = categoryValue.parentId;
        if (parentId) {
            return [parentId].concat(this._getAncestorValueIds(category, parentId));
        }
        return [];
    },
    /**
     * @private
     */
    _render: function () {
        var self = this;
        this.$el.empty();

        // sort categories and filters according to their index
        var categories = Object.keys(this.categories).map(function (categoryId) {
            return self.categories[categoryId];
        });
        var filters = Object.keys(this.filters).map(function (filterId) {
            return self.filters[filterId];
        });
        var sections = categories.concat(filters).sort(function (s1, s2) {
            return s1.index - s2.index;
        });

        sections.forEach(function (section) {
            if (Object.keys(section.values).length) {
                if (section.type === 'category') {
                    self.$el.append(self._renderCategory(section));
                } else {
                    self.$el.append(self._renderFilter(section));
                }
            }
        });
    },
    /**
     * @private
     * @param {Object} category
     * @returns {string}
     */
    _renderCategory: function (category) {
        return qweb.render('SearchPanel.Category', {category: category});
    },
    /**
     * @private
     * @param {Object} filter
     * @returns {jQuery}
     */
    _renderFilter: function (filter) {
        var $filter = $(qweb.render('SearchPanel.Filter', {filter: filter}));

        // set group inputs in indeterminate state when necessary
        Object.keys(filter.groups || {}).forEach(function (groupId) {
            var state = filter.groups[groupId].state;
            // group 'false' is not displayed
            if (groupId !== 'false' && state === 'indeterminate') {
                $filter
                    .find('.o_search_panel_filter_group[data-group-id=' + groupId + '] input')
                    .get(0)
                    .indeterminate = true;
            }
        });

        return $filter;
    },
    /**
     * Compute the current searchPanel domain based on categories and filters,
     * and notify environment of the domain change.
     *
     * Note that this assumes that the environment will update the searchPanel.
     * This is done as such to ensure the coordination between the reloading of
     * the searchPanel and the reloading of the data.
     *
     * @private
     */
    _notifyDomainUpdated: function () {
        this.needReload = true;
        this.trigger_up('search_panel_domain_updated', {
            domain: this.getDomain(),
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onCategoryValueClicked: function (ev) {
        ev.stopPropagation();
        var $item = $(ev.currentTarget).closest('.o_search_panel_category_value');
        var category = this.categories[$item.data('categoryId')];
        var valueId = $item.data('id') || false;
        category.activeValueId = valueId;
        var storageKey = this._getLocalStorageKey(category);
        this.call('local_storage', 'setItem', storageKey, valueId);
        this._notifyDomainUpdated();
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onFilterGroupChanged: function (ev) {
        ev.stopPropagation();
        var $item = $(ev.target).closest('.o_search_panel_filter_group');
        var filter = this.filters[$item.data('filterId')];
        var groupId = $item.data('groupId');
        var group = filter.groups[groupId];
        group.state = group.state === 'checked' ? 'unchecked' : 'checked';
        Object.keys(group.values).forEach(function (valueId) {
            group.values[valueId].checked = group.state === 'checked';
        });
        this._notifyDomainUpdated();
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onFilterValueChanged: function (ev) {
        ev.stopPropagation();
        var $item = $(ev.target).closest('.o_search_panel_filter_value');
        var valueId = $item.data('valueId');
        var filter = this.filters[$item.data('filterId')];
        var value = filter.values[valueId];
        value.checked = !value.checked;
        var group = filter.groups && filter.groups[value.group_id];
        if (group) {
            var valuePartition = _.partition(Object.keys(group.values), function (valueId) {
                return group.values[valueId].checked;
            });
            if (valuePartition[0].length && valuePartition[1].length) {
                group.state = 'indeterminate';
            } else if (valuePartition[0].length) {
                group.state = 'checked';
            } else {
                group.state = 'unchecked';
            }
        }
        this._notifyDomainUpdated();
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onToggleFoldCategory: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var $item = $(ev.currentTarget).closest('.o_search_panel_category_value');
        var category = this.categories[$item.data('categoryId')];
        var valueId = $item.data('id');
        category.values[valueId].folded = !category.values[valueId].folded;
        this._render();
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onToggleFoldFilterGroup: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var $item = $(ev.currentTarget).closest('.o_search_panel_filter_group');
        var filter = this.filters[$item.data('filterId')];
        var groupId = $item.data('groupId');
        filter.groups[groupId].folded = !filter.groups[groupId].folded;
        this._render();
    },
});

if (config.device.isMobile) {
    SearchPanel.include({
        tagName: 'details',

        _getCategorySelection: function () {
            var self = this;
            return Object.keys(this.categories).reduce(function (selection, categoryId) {
                var category = self.categories[categoryId];
                console.log('category', category);
                if (category.activeValueId) {
                    var ancestorIds = [category.activeValueId].concat(self._getAncestorValueIds(category, category.activeValueId));
                    var breadcrumb = ancestorIds.map(function (valueId) {
                        return category.values[valueId].display_name;
                    });
                    selection.push({ breadcrumb: breadcrumb, icon: category.icon, color: category.color});
                }
                console.log('selection', selection);
                return selection;
            }, []);
        },

        _getFilterSelection: function () {
            var self = this;
            return Object.keys(this.filters).reduce(function (selection, filterId) {
                var filter = self.filters[filterId];
                console.log('filter', filter);
                if (filter.groups) {
                    Object.keys(filter.groups).forEach(function (groupId) {
                        var group = filter.groups[groupId];
                        Object.keys(group.values).forEach(function (valueId) {
                            var value = group.values[valueId];
                            if (value.checked) {
                                selection.push({name: value.name, icon: filter.icon, color: filter.color});
                            }
                        });
                    });
                } else if (filter.values) {
                    Object.keys(filter.values).forEach(function (valueId) {
                        var value = filter.values[valueId];
                        if (value.checked) {
                            selection.push({name: value.name, icon: filter.icon, color: filter.color});
                        }
                    });
                }
                console.log('selection', selection);
                return selection;
            }, []);
        },

        _render: function () {
            this._super.apply(this, arguments);
            this.$el.prepend(qweb.render('SearchPanel.MobileSummary', {
                categories: this._getCategorySelection(),
                filterValues: this._getFilterSelection(),
                separator: ' / ',
            }));
        },
    });
}

return SearchPanel;

});