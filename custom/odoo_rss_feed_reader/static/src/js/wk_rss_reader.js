/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('odoo_rss_feed_reader.wk_rss_feed', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    $(document).ready(function() {
        if ($('.wk_content').length) {
            $("div#wk_loader").addClass('show');
            $(".wk_nav").css("-webkit-filter", 'blur(2px)');
            getRssPageData('');
            $('.rss_menu').on('click', function(e) {
                $("div#wk_loader").addClass('show');
                $(".rss_menu").removeClass("active");
                $(this).addClass("active");
                var rss = $(this).text();
                getRssPageData(rss);
            });

            $('body').on('change', '.wk_rss_menu', function(){
                $("div#wk_loader").addClass('show');
                $(".wk_snippet").css("-webkit-filter", 'blur(5px)');
                var rss = $(this).val();
                getRssPageData(rss);
            });
        }
    });


    function getRssPageData(rss) {
        ajax.jsonRpc("/get/rss/data", 'call', {'rss':rss})
        .then(function (data) {
            if (data.response == 'success') {
                $('.wk_content').html(data.data);
                $("div#wk_loader").removeClass('show');
            } else {
                $(".wk_snippet").remove();
                $('.wk_content').html('<div class="wk_sorry_page"><span class="fa fa-frown-o"> Sorry!</span></div>\
                                        <div style="\
                                        text-align: -webkit-center;\
                                        font-size: larger;\
                                    ">'+data.data+'</div>');
                $("div#wk_loader").removeClass('show');
            }
        })
    }
})
