/* eslint-disable */
odoo.define("pos_extra_products.DB", function (require) {
    "use strict";

    const PosDB = require("point_of_sale.DB");

    PosDB.include({
        init: function (options) {
            this._super(options);
            this.category_search_extra = {};
        },

        add_products: function (products) {
            /*
                Extend this methode to generate a string contain id of all products available in pos with  references
                (references_search_string), designation (designation_search_string), barcode (barcode_search_string)
                and grouped those product with category and stored in category_search_references_string,
                category_search_designation_string and category_search_barcode_string to use it for search.
            */
            var res = this._super(products);
            if (!products instanceof Array) {
                products = [products];
            }
            for (var i = 0, len = products.length; i < len; i++) {
                var product = products[i];
                if (product.available_in_pos) {
                    var categ_id = product.pos_categ_id
                        ? product.pos_categ_id[0]
                        : this.root_category_id;
                    if (this.category_search_extra[categ_id] === undefined) {
                        this.category_search_extra[categ_id] = [];
                    }
                    if (product.is_extra) {
                        this.category_search_extra[categ_id].push(product.id);
                    }
                    var ancestors = this.get_category_ancestors_ids(categ_id) || [];
                    for (var j = 0, jlen = ancestors.length; j < jlen; j++) {
                        var ancestor = ancestors[j];
                        if (!this.category_search_extra[ancestor]) {
                            this.category_search_extra[ancestor] = [];
                        }
                        if (product.is_extra) {
                            this.category_search_extra[ancestor].push(product.id);
                        }
                    }
                }
            }
        },

        search_extra_product_in_category: function (category_id, query) {
            // Make search for extra products in specific category
            var results = [];
            if (category_id) {
                for (
                    var j = 0;
                    j < this.category_search_extra[category_id].length;
                    j++
                ) {
                    if (this.category_search_extra[category_id][j]) {
                        var id = Number(this.category_search_extra[category_id][j]);
                        results.push(this.get_product_by_id(id));
                    } else {
                        break;
                    }
                }
            }
            return results;
        },

        get_product_by_category: function (category_id) {
            var product_ids = this.product_by_category_id[category_id];
            var list = [];
            if (product_ids) {
                for (
                    var i = 0, len = Math.min(product_ids.length, this.limit);
                    i < len;
                    i++
                ) {
                    if (!this.product_by_id[product_ids[i]].is_extra) {
                        list.push(this.product_by_id[product_ids[i]]);
                    }
                }
            }
            return list;
        },
    });

    return PosDB;
});
