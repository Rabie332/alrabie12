/* eslint-disable */
odoo.define("islamic_datepicker.form_view_date", function (require) {
    var BasicRenderer = require("web.BasicRenderer");
    var core = require("web.core");
    var field_utils = require("web.field_utils");
    var registry = require("web.field_registry");
    var date_picker = require("web.datepicker");
    var data = require("web.data");
    var time = require("web.time");
    var utils = require("web.utils");
    var _t = core._t;
    var lang = "ar";
    var date_format = "yy-mm-dd".replace(/%(.)/g, "$1$1").toLowerCase();
    date_picker.DateWidget.include({
        /**
         * @override this method to provoc an error when updating a date field
         */
        destroy: function () {
            if (this.picker) {
                this.picker.destroy();
            }
        },
        /**
         *Override this method to prevent showing hindi digits in date
         */
        setValue: function (value) {
            this._super.apply(this, arguments);
            this.set({value: value});
            var formatted_value = value ? this._formatClient(value) : null;
            var hijri_date = this.get_hijri_gregorian();
            this.$input_hijri.val(hijri_date);
            this.$input.val(formatted_value);
            if (this.picker) {
                this.picker.date(value || null);
            }
        },
        start: function () {
            this._super.apply(this, arguments);
            var self = this;
            this.$input_hijri = this.$el.find("input.oe_hijri");
            this.$input = this.$el.find("input.o_datepicker_input");
            if (this.options.locale == "ar") {
                this.$input.css({"margin-right": "15px"});
            } else {
                this.$input.css({"margin-left": "15px"});
            }
            this.$input.datetimepicker(this.options);
            this.picker = this.$input.data("DateTimePicker");
            function convert_date_hijri(date_p) {
                if (!date_p) {
                    return false;
                }
                if (self.type_of_date == "date") {
                    var jd = $.calendars
                        .instance("ummalqura")
                        .toJD(
                            parseInt(date_p[0]._year),
                            parseInt(date_p[0]._month),
                            parseInt(date_p[0]._day)
                        );
                    var date = $.calendars.instance("gregorian").fromJD(jd);
                    var date_value = new Date(
                        parseInt(date.year()),
                        parseInt(date.month()) - 1,
                        parseInt(date.day())
                    );
                    self.$input.val(
                        $.datepicker.formatDate(date_format, date_value)
                    );
                }
                self.changeDatetime();
            }
            this.$input_hijri.calendarsPicker({
                // ShowAnim: 'slide'
                showSpeed: 300,
                firstDay: 7,
                showOptions: {
                    direction: "horizontal",
                },
                defaultDate: self.get_hijri_gregorian(),
                selectDefaultDate: true,
                calendar: $.calendars.instance("ummalqura", lang),
                dateFormat: "yyyy-mm-dd",
                onSelect: convert_date_hijri,
                pickerClass: "calandar_picker",
                isRTL: true,
                renderer: $.extend({}, $.calendarsPicker.defaultRenderer, {
                    picker: $.calendarsPicker.defaultRenderer.picker.replace(
                        /\{link:clear\}/,
                        ""
                    ),
                }),
            });
            this.$input_hijri.click(function (event) {
                event.stopPropagation();
                $(".oe_hijri").calendarsPicker({
                    // ShowAnim: 'slide'
                    showSpeed: 300,
                    firstDay: 7,
                    showOptions: {
                        direction: "horizontal",
                    },
                    selectDefaultDate: true,
                    calendar: $.calendars.instance("ummalqura", lang),
                    dateFormat: "yyyy-mm-dd",
                    onSelect: convert_date_hijri,
                    pickerClass: "calandar_picker",
                    isRTL: true,
                    renderer: $.extend({}, $.calendarsPicker.defaultRenderer, {
                        picker: $.calendarsPicker.defaultRenderer.picker.replace(
                            /\{link:clear\}/,
                            ""
                        ),
                    }),
                });
            });
            this.setValue(this.getValue());
        },
        convert_gregorian_hijri: function (text) {
            if (text) {
                calendar = $.calendars.instance("gregorian");
                calendar1 = $.calendars.instance("ummalqura");
                text = moment(text, date_format)._i;
                if (text.indexOf("-") != -1) {
                    text_split = text.split("-");
                    year = parseInt(text_split[0]);
                    month = parseInt(text_split[1]);
                    day = parseInt(text_split[2]);
                    var jd = $.calendars
                        .instance("gregorian")
                        .toJD(year, month, day);
                    var date = $.calendars.instance("ummalqura").fromJD(jd);
                }
                if (text.indexOf("/") != -1) {
                    text_split = text.split("/");
                    year = parseInt(text_split[2]);
                    month = parseInt(text_split[0]);
                    day = parseInt(text_split[1]);
                    calendar = $.calendars.instance("gregorian");
                    calendar1 = $.calendars.instance("ummalqura");
                    var jd = calendar.toJD(year, month, day);
                    var date = calendar1.fromJD(jd);
                }
                if (calendar1) {
                    return calendar1.formatDate("yyyy-mm-dd", date);
                }
            }
            return "";
        },
        get_hijri_gregorian: function () {
            var text = this.getValue();
            if (text) {
                calendar = $.calendars.instance("gregorian");
                calendar1 = $.calendars.instance("ummalqura");
                date_text = moment(text, date_format);
                year = parseInt(date_text.year());
                month = parseInt(date_text.month()) + 1;
                day = parseInt(date_text.date());
                var jd = calendar.toJD(year, month, day);
                var hijri_date = calendar1.fromJD(jd);
                return calendar1.formatDate("yyyy-mm-dd", hijri_date);
            }
            return "";
        },
        _onDateTimePickerShow: function () {
            this._super.apply(this, arguments);
            this.$input_hijri.val("");
        },
    });

    /**
     * @override
     */
    BasicRenderer.include({
        convert_gregorian_hijri: function (text) {
            if (text) {
                text = moment(text, date_format)._i;
                calendar1 = $.calendars.instance("ummalqura");
                if (text.indexOf("-") != -1) {
                    text_split = text.split("-");
                    year = parseInt(text_split[0]);
                    month = parseInt(text_split[1]);
                    day = parseInt(text_split[2]);
                    calendar = $.calendars.instance("gregorian");
                    calendar1 = $.calendars.instance("ummalqura");
                    var jd = $.calendars
                        .instance("gregorian")
                        .toJD(year, month, day);
                    var date = $.calendars.instance("ummalqura").fromJD(jd);
                }
                if (text.indexOf("/") != -1) {
                    text_split = text.split("/");
                    year = parseInt(text_split[2]);
                    month = parseInt(text_split[0]);
                    day = parseInt(text_split[1]);
                    calendar = $.calendars.instance("gregorian");
                    calendar1 = $.calendars.instance("ummalqura");
                    var jd = calendar.toJD(year, month, day);
                    var date = calendar1.fromJD(jd);
                }
                if (calendar1) {
                    return calendar1.formatDate("yyyy-mm-dd", date);
                }
            }
            return "";
        },
        /**
         * @override _postProcessField method
         * 1- in case of the form is in readonly mode we must show for every date or datetime field it's corresponding hijri date.
         */
        _postProcessField: function (widget, node) {
            this._super.apply(this, arguments);
            var name = node.attrs.name;
            var field = this.state.fields[name];
            if (field && field.type) {
                var value = widget.record.data[name];
                var formattedValue = field_utils.format[field.type](
                    value,
                    field,
                    {
                        data: widget.record.data,
                        escape: true,
                        isPassword: "password" in node.attrs,
                    }
                );
                if (field.type === "date" && typeof value._i !== "undefined") {
                    var hijri_date = this.convert_gregorian_hijri(value._i);
                    if (this.mode == "edit") {
                        $(this.$el.find("input.oe_hijri")).val(hijri_date);
                    }
                    if (
                        this.mode == "readonly" ||
                        (this.mode == "edit" &&
                            widget.$el.hasClass("o_readonly_modifier"))
                    ) {
                        formattedValue = value._i + " / " + hijri_date;
                        if (!widget.$el.parent().hasClass("o_field_cell")) {
                            widget.$el.text(formattedValue);
                        }
                    }
                }
            }
        },
    });
});
