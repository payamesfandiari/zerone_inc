/* Project specific Javascript goes here. */
!function (o) {
    "use strict";
    o('a.js-scroll-trigger[href*="#"]:not([href="#"])').click((function () {
        if (location.pathname.replace(/^\//, "") == this.pathname.replace(/^\//, "") && location.hostname == this.hostname) {
            var a = o(this.hash);
            if ((a = a.length ? a : o("[name=" + this.hash.slice(1) + "]")).length) return o("html, body").animate({scrollTop: a.offset().top - 70}, 1e3, "easeInOutExpo"), !1
        }
    })), o(document).scroll((function () {
        o(this).scrollTop() > 100 ? o(".scroll-to-top").fadeIn() : o(".scroll-to-top").fadeOut()
    })), o(".js-scroll-trigger").click((function () {
        o(".navbar-collapse").collapse("hide")
    })), o("body").scrollspy({target: "#mainNav", offset: 80});
    var a = function () {
        o("#mainNav").offset().top > 100 ? o("#mainNav").addClass("navbar-shrink") : o("#mainNav").removeClass("navbar-shrink")
    };
    a(), o(window).scroll(a), o((function () {
        o("body").on("input propertychange", ".floating-label-form-group", (function (a) {
            o(this).toggleClass("floating-label-form-group-with-value", !!o(a.target).val())
        })).on("focus", ".floating-label-form-group", (function () {
            o(this).addClass("floating-label-form-group-with-focus")
        })).on("blur", ".floating-label-form-group", (function () {
            o(this).removeClass("floating-label-form-group-with-focus")
        }))
    }))
}(jQuery);
