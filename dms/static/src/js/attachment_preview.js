odoo.define("dms.data_preview", function (require) {
    "use strict";

    var FieldBinaryFile = require("web.basic_fields").FieldBinaryFile;
    var field_registry = require("web.field_registry");
    var utils = require("web.utils");
    var core = require("web.core");
    var _t = core._t;

    var FieldViewer = FieldBinaryFile.extend({
        supportedFieldTypes: ["binary"],
        template: "FieldViewer",
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.PDFViewerApplication = false;
        },

        // --------------------------------------------------------------------------
        // Private
        // --------------------------------------------------------------------------

        /**
         * @private
         * @param {DOMElement} iframe
         */
        _disableButtons: function (iframe) {
            $(iframe).contents().find("button#openFile").hide();
        },
        /**
         * @private
         * @param {String} [fileURI] file URI if specified
         * @returns {String} the pdf viewer URI
         */
        _getURI: function (fileURI) {
            var page = this.recordData[this.name + "_page"] || 1;
            var tempFileURI = false;
            if (fileURI) {
                tempFileURI = fileURI;
            } else {
                var queryObj = {
                    model: this.model,
                    field: this.name,
                    id: this.res_id,
                };
                var queryString = $.param(queryObj);
                tempFileURI = "/web/content?" + queryString;
            }
            var FinalFileURI = encodeURIComponent(tempFileURI);
            var viewerURL = "/web/static/lib/pdfjs/web/viewer.html?file=";
            return viewerURL + FinalFileURI + "#page=" + page;
        },
        /**
         * @private
         * @override
         * Render just pdf or image
         */
        _render: function () {
            var self = this;
            if (this.recordData.extension === ".pdf") {
                var $pdfViewer = this.$(".o_form_pdf_controls")
                    .children()
                    .add(this.$(".o_pdfview_iframe"));
                var $selectUpload = this.$(".o_select_file_button").first();
                var $iFrame = this.$(".o_pdfview_iframe");

                $iFrame.on("load", function () {
                    self.PDFViewerApplication = this.contentWindow.window.PDFViewerApplication;
                    self._disableButtons(this);
                });
                if (this.mode === "readonly" && this.value) {
                    $iFrame.attr("src", this._getURI());
                } else if (this.value) {
                    var binSize = utils.is_bin_size(this.value);
                    $pdfViewer.removeClass("o_hidden");
                    $selectUpload.addClass("o_hidden");
                    if (binSize) {
                        $iFrame.attr("src", this._getURI());
                    }
                } else {
                    $pdfViewer.addClass("o_hidden");
                    $selectUpload.removeClass("o_hidden");
                }
            } else if (
                [".png", ".jpe", ".gif", ".ico"].indexOf(this.recordData.extension) > -1
            ) {
                this.$el.empty().append(
                    $("<img/>", {
                        src:
                            "/web/image/" +
                            this.model +
                            "/" +
                            this.record.data.id +
                            "/" +
                            this.name +
                            "?unique=1",
                        title: this.record.data.display_name,
                        style: "max-width:100%;",
                        alt: _t("Image"),
                    })
                );
            }
        },

        // --------------------------------------------------------------------------
        // Handlers
        // --------------------------------------------------------------------------

        /**
         * @override
         * @private
         * @param {Event} ev
         */
        on_file_change: function (ev) {
            this._super.apply(this, arguments);
            var files = ev.target.files;
            if (!files || files.length === 0) {
                return;
            }
            // TOCheck: is there requirement to fallback on FileReader if browser don't support URL
            var fileURI = URL.createObjectURL(files[0]);
            if (this.PDFViewerApplication) {
                this.PDFViewerApplication.open(fileURI, 0);
            } else {
                this.$(".o_pdfview_iframe").attr("src", this._getURI(fileURI));
            }
        },
        /**
         * Remove the behaviour of on_save_as in FieldBinaryFile.
         *
         * @override
         * @private
         * @param {MouseEvent} ev
         */
        on_save_as: function (ev) {
            ev.stopPropagation();
        },
    });

    field_registry.add("data_preview", FieldViewer);

    return FieldViewer;
});
