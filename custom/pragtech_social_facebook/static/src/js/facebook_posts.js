odoo.define('pragtech_social_facebook.all_posts', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var field_utils = require('web.field_utils');
var dom = require('web.dom');

var FacebookPosts = AbstractAction.extend({
    contentTemplate: 'FBPostsMainMenu',
    events: {
        "click .post_button": 'postButton',
    },

    postButton: function (ev) {
        ev.preventDefault();
        var inputCheckBox = document.getElementsByName("AccountCheckBox");
        var post_message = document.getElementsByName("PostMessage")[0].value;
        var image = document.getElementById('previewImg')
        var image_src = '';
        if (image && image.src) {
            image_src = image.src
        }
        var account_ids = [];
        for( var i = 0; i < inputCheckBox.length; i ++ ) {
            if (inputCheckBox[i].checked) {
                account_ids.push(parseInt(inputCheckBox[i].id));
            }
        }
        if (post_message == ''){
            alert("Please Enter the Post Message!")
            return
        }
        if (account_ids.length === 0){
            alert("Please Select at least one Page!")
            return
        }
        var def = this._rpc({
                model: 'pragtech.social.account',
                method: 'post_data',
                args: [false, account_ids, post_message, image.src],
            })
            .then(function (res) {
                if (res) {
                    location.reload();
                }
            });
   },
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
                model: 'pragtech.social.post',
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

            var inputReplyInnerComments = document.getElementsByName("inputReplyInnerComments");
            for( var i = 0; i < inputReplyInnerComments.length; i ++ ) {
                if (inputReplyInnerComments[i].value) {
                    var def = this._rpc({
                        model: 'pragtech.social.stream.post',
                        method: 'post_comments',
                        args: [false, inputReplyInnerComments[i].id, inputReplyInnerComments[i].value, 'InnerReply'],
                    })
                    .then(function (res) {
                        if (res) {
                            location.reload();
                        }
                    });
                }
            }
        }
    },

    willStart: function () {
        var self = this;
        var def = this._rpc({
                model: 'pragtech.social.account',
                method: 'search_read',
                args: [[['social_m_type', '=', 'facebook']], []],
            })
            .then(function (res) {
                self.account_ids = res //res.length && res[0];
            });

        return Promise.all([def, this._super.apply(this, arguments)]);
    },
});

core.action_registry.add('facebook_posts', FacebookPosts);

return FacebookPosts;

});
