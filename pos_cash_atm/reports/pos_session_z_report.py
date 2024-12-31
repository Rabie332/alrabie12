from datetime import datetime, timedelta

import pytz
from pytz import timezone

from odoo import SUPERUSER_ID, models


class PosSession(models.Model):
    _inherit = "pos.session"

    def get_report_timezone(self):
        if self.env.user and self.env.user.tz:
            tz = timezone(self.env.user.tz)
        else:
            tz = pytz.utc
        return tz

    def get_session_date(self, date_time):
        if date_time:
            if self.env.user and self.env.user.tz:
                tz = timezone(self.env.user.tz)
            else:
                tz = pytz.utc
            c_time = datetime.now(tz)
            hour_tz = int(str(c_time)[-5:][:2])
            min_tz = int(str(c_time)[-5:][3:])
            sign = str(c_time)[-6][:1]
            if sign == "+":
                date_time = date_time + timedelta(hours=hour_tz, minutes=min_tz)
            else:
                date_time = date_time - timedelta(hours=hour_tz, minutes=min_tz)
            return date_time.strftime("%d/%m/%Y %I:%M:%S %p")

    def get_session_time(self, date_time):
        if date_time:
            if self.env.user and self.env.user.tz:
                tz = timezone(self.env.user.tz)
            else:
                tz = pytz.utc
            c_time = datetime.now(tz)
            hour_tz = int(str(c_time)[-5:][:2])
            min_tz = int(str(c_time)[-5:][3:])
            sign = str(c_time)[-6][:1]
            if sign == "+":
                date_time = date_time + timedelta(hours=hour_tz, minutes=min_tz)
            else:
                date_time = date_time - timedelta(hours=hour_tz, minutes=min_tz)
            return date_time.strftime("%I:%M:%S %p")

    def get_inventory_details(self):
        product_product = self.env["product.product"]
        stock_location = self.config_id.stock_location_id
        inventory_records = []
        final_list = []
        product_details = []
        for line in self.order_ids.mapped("lines"):
            product_details.append({"id": line.product_id.id, "qty": line.qty})
        custom_list = []
        for each_prod in product_details:
            if each_prod.get("id") not in [x.get("id") for x in custom_list]:
                custom_list.append(each_prod)
            else:
                for each in custom_list:
                    if each.get("id") == each_prod.get("id"):
                        each.update({"qty": each.get("qty") + each_prod.get("qty")})
        for each in custom_list:
            product_id = product_product.browse(each.get("id"))
            if product_id:
                inventory_records.append(
                    {
                        "product_id": [product_id.id, product_id.name],
                        "category_id": [product_id.id, product_id.categ_id.name],
                        "used_qty": each.get("qty"),
                        "quantity": product_id.with_context(
                            {"location": stock_location.id, "compute_child": False}
                        ).qty_available,
                        "uom_name": product_id.uom_id.name or "",
                    }
                )
            if inventory_records:
                temp_list = []
                temp_obj = []
                for each in inventory_records:
                    if each.get("product_id")[0] not in temp_list:
                        temp_list.append(each.get("product_id")[0])
                        temp_obj.append(each)
                    else:
                        for rec in temp_obj:
                            if rec.get("product_id")[0] == each.get("product_id")[0]:
                                qty = rec.get("quantity") + each.get("quantity")
                                rec.update({"quantity": qty})
                final_list = sorted(temp_obj, key=lambda k: k["quantity"])
        return final_list or []

    def get_user(self):
        if self._uid == SUPERUSER_ID:
            return True

    def get_product_cate_total(self):
        balance_end_real = 0.0
        for line in self.order_ids.mapped("lines"):
            balance_end_real += line.qty * line.price_unit
        return balance_end_real

    def get_product_name(self, category_id):
        if category_id:
            category_name = self.env["pos.category"].browse([category_id]).name
            return category_name

    def get_product_category(self):
        product_list = []
        for line in self.order_ids.mapped("lines"):
            flag = False
            product_dict = {}
            for lst in product_list:
                if line.product_id.pos_categ_id:
                    if lst.get("pos_categ_id") == line.product_id.pos_categ_id.id:
                        lst["price"] = lst["price"] + (line.qty * line.price_unit)
                        flag = True
                else:
                    if lst.get("pos_categ_id") == "":
                        lst["price"] = lst["price"] + (line.qty * line.price_unit)
                        flag = True
            if not flag:
                product_dict.update(
                    {
                        "pos_categ_id": line.product_id.pos_categ_id
                        and line.product_id.pos_categ_id.id
                        or "",
                        "price": (line.qty * line.price_unit),
                    }
                )
                product_list.append(product_dict)
        return product_list
