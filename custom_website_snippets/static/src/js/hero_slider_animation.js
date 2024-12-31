odoo.define("custom_website_snippets.heroSliderAnimation", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");

    publicWidget.registry.heroSlider = publicWidget.Widget.extend({
        selector: ".hero-slider",
        start: function () {
            this._super.apply(this, arguments);
            this.initSlider();
        },
        initSlider: function () {
            const slides = this.$el.find(".slide");
            let currentSlide = 0;

            function showSlide(index) {
                slides.each((idx, slide) => {
                    $(slide).css("opacity", idx === index ? "1" : "0");
                });
            }

            function nextSlide() {
                currentSlide = (currentSlide + 1) % slides.length;
                showSlide(currentSlide);
            }

            setInterval(nextSlide, 4000); // Change slide every 10 seconds
            showSlide(currentSlide); // Initialize the first slide

            this.initDynamicText();
        },
        initDynamicText: function () {
            const dynamicTextWrapper = this.$el.find("#dynamic-text-wrapper");
            const dynamicText = dynamicTextWrapper.find("#dynamic-text");
            dynamicText.text(""); // Reset dynamic text at the start
            const texts = ["create", "innovate", "accelerate"];
            let currentText = 0;

            async function typeText(text) {
                for (let char of text) {
                    await new Promise((resolve) => {
                        setTimeout(() => {
                            dynamicText.text(dynamicText.text() + char);
                            resolve();
                        }, 200); // Speed of typing each character
                    });
                }
            }

            async function changeText() {
                await typeText(texts[currentText]);
                // dynamicTextWrapper.removeClass(); // Reset classes
                // dynamicTextWrapper.addClass(`bg-color-${currentText + 1}`);

                await new Promise((resolve) =>
                    setTimeout(() => {
                        dynamicText.html("&nbsp;"); // Use .html() to insert HTML content
                        resolve();
                    }, 2000)
                ); // Wait before changing text

                currentText = (currentText + 1) % texts.length;
                dynamicText.text(""); // Clear text for next word

                changeText(); // Start typing next word
            }

            changeText(); // Initialize the dynamic text typing
        },
    });
});
