odoo.define("custom_website_snippets.swiper_js", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");

    publicWidget.registry.FarhaSwiper = publicWidget.Widget.extend({
        selector: ".s_farha_swiper",
        events: {
            "click .swiper-button-next": "_onClickNext",
            "click .swiper-button-prev": "_onClickPrev",
        },

        start: function () {
            this.$slides = this.$(".swiper-slide");
            this.currentSlide = 0;
            this.slidesPerView = 3; // Set the number of slides to show at once
            this._showSlides(); // Show initial slides
        },

        _showSlides: function () {
            this.$slides.removeClass("active").hide(); // Hide all slides
            // Show only the slides for the current index
            this.$slides
                .slice(this.currentSlide, this.currentSlide + this.slidesPerView)
                .addClass("active")
                .css("display", "block");
        },

        _onClickNext: function () {
            // Increment slides, wrap around using modulo
            this.currentSlide =
                (this.currentSlide + this.slidesPerView) % this.$slides.length;
            this._showSlides();
        },

        _onClickPrev: function () {
            // Decrement slides, wrap around correctly
            this.currentSlide =
                (this.currentSlide - this.slidesPerView + this.$slides.length) %
                this.$slides.length;
            this._showSlides();
        },
    });
});
