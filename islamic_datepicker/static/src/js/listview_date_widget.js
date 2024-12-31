/* eslint-disable */
odoo.define("islamic_datepicker.list_view_date", function (require) {
    var core = require("web.core");
    var ListRenderer = require("web.ListRenderer");
    var field_utils = require("web.field_utils");
    var data = require("web.data");
    var date_format = "%Y-%m-%d".replace(/%(.)/g, "$1$1").toLowerCase();

    /**
     * @override
     */
    ListRenderer.include({
        _renderBodyCell: function (record, node, colIndex, options) {
            var $cell = this._super.apply(this, arguments);
            var name = node.attrs.name;
            var field = this.state.fields[name];
            var value = record.data[name];
            if (field) {
                var formattedValue = field_utils.format[field.type](
                    value,
                    field,
                    {
                        data: record.data,
                        escape: true,
                        isPassword: "password" in node.attrs,
                    }
                );
                // Render Islamic hijri umalqura date
                if (field.type === "date" && typeof value._i !== "undefined") {
                    var formattedValue =
                        this.convert_gregorian_hijri(value._i) +
                        " / " +
                        value._i;
                    if (options.mode === "readonly") {
                        $cell.text(formattedValue);
                    }
                }
            }
            return $cell;
        },
        convert_gregorian_hijri: function (text) {
            if (text) {
                var calendar1 = $.calendars.instance("ummalqura");
                text = moment(text, date_format)._i;
                if (text.indexOf("-") != -1) {
                    text_split = text.split("-");
                    year = parseInt(text_split[0]);
                    month = parseInt(text_split[1]);
                    day = parseInt(text_split[2]);
                    calendar = $.calendars.instance("gregorian");

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

                    var jd = calendar.toJD(year, month, day);
                    var date = calendar1.fromJD(jd);
                }

                return calendar1.formatDate("yyyy-mm-dd", date);
            }
            return "";
        },
    });
});
