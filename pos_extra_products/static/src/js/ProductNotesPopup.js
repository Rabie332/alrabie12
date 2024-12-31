odoo.define("pos_extra_products.ProductNotesPopup", function (require) {
    "use strict";

    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const Registries = require("point_of_sale.Registries");
    const {useState, useRef} = owl.hooks;
    const {useListener} = require("web.custom_hooks");

    // Formerly ProductNotesPopup
    class ProductNotesPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this.state = useState({inputValue: this.props.startingValue});
            this.inputRef = useRef("input");
            useListener("change-product-notes", this._ChangeProductNotes);
        }
        mounted() {
            this.inputRef.el.focus();
        }
        getPayload() {
            return this.state.inputValue;
        }
        _ChangeProductNotes(event) {
            this.state.inputValue =
                event.target.options[event.target.selectedIndex].text;
        }
    }
    ProductNotesPopup.template = "ProductNotesPopup";
    ProductNotesPopup.defaultProps = {
        confirmText: "Ok",
        title: "Confirm ?",
        body: "",
    };

    Registries.Component.add(ProductNotesPopup);

    return ProductNotesPopup;
});
