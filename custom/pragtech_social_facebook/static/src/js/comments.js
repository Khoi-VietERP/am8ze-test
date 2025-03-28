odoo.define('pragtech_social_facebook.all_comments', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var field_utils = require('web.field_utils');
var dom = require('web.dom');

var AllComments = AbstractAction.extend({
    contentTemplate: 'FBCommentsMainMenu',
    events: {
        "click .likeMainComment": 'mainCommentLike',
        "click .likeMainCommentComment": 'likeMainCommentComment',
        "click .likeMainCommentCommentInner": "likeMainCommentCommentInner",
        'click .mainCommentReplyText': 'mainCommentReply',
//        'click .mainInnerCommentReply': 'mainInnerCommentReply',
        'click .buttonRefresh': 'buttonRefresh',
        'click .buttonPostWindows': 'buttonPostWindows',
        'click .loadmore': 'buttonLoadMore',
        'click .commentInput': 'commentInput',
        'click .loadmorepost': 'buttonLoadMorePost',
        'click .PageCheckBox': 'pageCheckBox',
    },

    pageCheckBox: function (ev) {
        ev.preventDefault();
        this._rpc({
                model: 'pragtech.social.stream',
                method: 'write',
                args: [ev.currentTarget.id, {view_fb_page_data: ev.currentTarget.checked}]
            })
            .then(function (res) {
                if (res) {
                    location.reload();
                }
            });
    },

    commentInput: function (ev) {
        ev.preventDefault();
        var inputID = 'input[id=' + ev.currentTarget.id + "]";
        $(inputID).focus();
    },

    buttonLoadMorePost: function (ev) {
        ev.preventDefault();
        $('.postClassDisplay:hidden').slice(0, 10).show(); // select next 10 hidden and show them
        var lengthHidden = $('.postClassDisplay:hidden').length;
        var marginpx = (lengthHidden * 10) - 5
        $('.loadmorepost').attr({'style': 'margin-top:' + -(marginpx) + 'px;background-color: white;'});
        if (lengthHidden <= 0){ // check if any hidden still exist
            $('.loadmorepost').hide();
        }
    },

    buttonLoadMore: function (ev) {
        ev.preventDefault();
        var inputID = 'div[id=' + ev.currentTarget.id + "]" + ".InnerCommentReplyMainClassDisplay:hidden";
        $(inputID).slice(0, 2).show(); // select next 2 hidden and show them
        var lengthHidden = $(inputID).length;
        if (lengthHidden <= 0){ // check if any hidden still exist
            var hideButton = 'a[id=' + ev.currentTarget.id + "]" + ".loadmore";
            $(hideButton).hide();
        }
    },

    buttonPostWindows: function (ev) {
        ev.preventDefault();
        this.do_action({
            type: 'ir.actions.client',
            tag: 'facebook_posts',
            name: 'Posts',
        });
    },

    buttonRefresh: function (ev) {
        ev.preventDefault();
        var def = this._rpc({
                model: 'pragtech.social.stream.post',
                method: 'sync_comments_post',
                args: [],
            })
            .then(function (res) {
                if (res) {
                    location.reload();
                }
            });
    },

//    mainInnerCommentReply: function (ev) {
//        ev.preventDefault();
//        var $target = $(ev.currentTarget);
//        var inputID = 'input[id=' + ev.currentTarget.id + "]";
//        $(inputID).toggle();
//        $(inputID).focus();
//   },

    mainCommentReply: function (ev) {
        ev.preventDefault();
        var $target = $(ev.currentTarget);
        var inputID = 'input[id=' + ev.currentTarget.id + "]";
        $(inputID).toggle();
        $(inputID).focus();
    },

    likeMainCommentCommentInner: function (ev) {
        ev.preventDefault();
        var def = this._rpc({
                model: 'pragtech.social.stream.post',
                method: 'inner_comments_likes',
                args: [false, ev.currentTarget.id],
            })
            .then(function (res) {
                if (res) {
                    location.reload();
                }
            });
        $(this).find('i').toggleClass("fa-thumbs-o-up fa-thumbs-o-up-down");
    },

    likeMainCommentComment: function (ev) {
        ev.preventDefault();
        var def = this._rpc({
                model: 'pragtech.social.stream.post',
                method: 'comments_likes',
                args: [false, ev.currentTarget.id],
            })
            .then(function (res) {
                if (res) {
                    location.reload();
                }
            });
        $(this).find('i').toggleClass("fa-thumbs-o-up fa-thumbs-o-up-down");
    },

    mainCommentLike: function (ev) {
        ev.preventDefault();
        $(this).toggleClass('active');
        var flag;
        var def = this._rpc({
                model: 'pragtech.social.stream.post',
                method: 'post_likes',
                args: [false, ev.currentTarget.id, flag],
            })
            .then(function (res) {
                if (res) {
                    location.reload();
                }
            });
    },

    _onKeyDown: function (event) {
        var self = this;
        var keyCode = event.keyCode;
        if (keyCode === 13) {
            event.preventDefault();
            var inputComments = document.getElementsByName("inputComments");
            for( var i = 0; i < inputComments.length; i ++ ) {
                if (inputComments[i].value) {
                    var def = this._rpc({
                        model: 'pragtech.social.stream.post',
                        method: 'post_comments',
                        args: [false, inputComments[i].id, inputComments[i].value, 'Comment'],
                    })
                    .then(function (res) {
                        if (res) {
                            location.reload();
                        }
                    });
                }
            }

            var inputReplyComments = document.getElementsByName("inputReplyComments");
            for( var i = 0; i < inputReplyComments.length; i ++ ) {
                if (inputReplyComments[i].value) {
                    var def = this._rpc({
                        model: 'pragtech.social.stream.post',
                        method: 'post_comments',
                        args: [false, inputReplyComments[i].id, inputReplyComments[i].value, 'Reply'],
                    })
                    .then(function (res) {
                        if (res) {
                            location.reload();
                        }
                    });
                }
            }

//            var inputReplyInnerComments = document.getElementsByName("inputReplyInnerComments");
//            for( var i = 0; i < inputReplyInnerComments.length; i ++ ) {
//                if (inputReplyInnerComments[i].value) {
//                    var def = this._rpc({
//                        model: 'pragtech.social.stream.post',
//                        method: 'post_comments',
//                        args: [false, inputReplyInnerComments[i].id, inputReplyInnerComments[i].value, 'InnerReply'],
//                    })
//                    .then(function (res) {
//                        if (res) {
//                            location.reload();
//                        }
//                    });
//                }
//            }
        }
    },

    willStart: function () {
        var self = this;
        $(document).on('keydown', self._onKeyDown.bind(self));
        $('.inputReplyComments').hide();
        $('.inputReplyInnerComments').hide();
        var def = this._rpc({
                model: 'pragtech.social.stream.post',
                method: 'get_all_datas',
                args: [[]],
            })
            .then(function (res) {
                self.post_ids = res[0]
                self.page_ids = res[1]
            });

        return Promise.all([def, this._super.apply(this, arguments)]);
    },
});

core.action_registry.add('facebook_comments', AllComments);

return AllComments;

});
