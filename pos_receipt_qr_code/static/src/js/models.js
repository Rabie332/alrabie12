odoo.define("pos_receipt_qr_code.pos", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var order_model_super = models.Order.prototype;
    models.load_fields("res.company", ["street", "city"]);

    models.Order = models.Order.extend({
        export_for_printing: function () {
            var receipt = order_model_super.export_for_printing.bind(this)();

            receipt = _.extend(receipt, {
                company: _.extend(receipt.company, {
                    street: this.pos.company.street,
                    city: this.pos.company.city,
                }),
            });
            const codeWriter = new window.ZXing.BrowserQRCodeSvgWriter();
            const qr_values = this.compute_sa_qr_code(
                receipt.company.name,
                receipt.company.vat,
                receipt.date.isostring,
                receipt.total_with_tax,
                receipt.total_tax
            );
            const qr_code_svg = new XMLSerializer().serializeToString(
                codeWriter.write(qr_values, 150, 150)
            );
            receipt.qr_code = "data:image/svg+xml;base64," + window.btoa(qr_code_svg);
            return receipt;
        },

        compute_sa_qr_code(name, vat, date_isostring, amount_total, amount_tax) {
            /* Generate the qr code for Saudi e-invoicing. Specs are available at the following link at page 23
        https://zatca.gov.sa/ar/E-Invoicing/SystemsDevelopers/Documents/20210528_ZATCA_Electronic_Invoice_Security_Features_Implementation_Standards_vShared.pdf
        */
            const seller_name_enc = this._compute_qr_code_field(1, name);
            const company_vat_enc = this._compute_qr_code_field(2, vat);
            const timestamp_enc = this._compute_qr_code_field(3, date_isostring);
            const invoice_total_enc = this._compute_qr_code_field(
                4,
                amount_total.toString()
            );
            const total_vat_enc = this._compute_qr_code_field(5, amount_tax.toString());

            const str_to_encode = seller_name_enc.concat(
                company_vat_enc,
                timestamp_enc,
                invoice_total_enc,
                total_vat_enc
            );

            let binary = "";
            for (let i = 0; i < str_to_encode.length; i++) {
                binary += String.fromCharCode(str_to_encode[i]);
            }
            return btoa(binary);
        },

        _compute_qr_code_field(tag, field) {
            const textEncoder = new TextEncoder();
            const name_byte_array = Array.from(textEncoder.encode(field));
            const name_tag_encoding = [tag];
            const name_length_encoding = [name_byte_array.length];
            return name_tag_encoding.concat(name_length_encoding, name_byte_array);
        },
    });
});
