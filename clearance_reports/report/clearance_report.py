from datetime import datetime

from odoo import api, fields, models


class ClearanceReport(models.TransientModel):
    _name = "clearance.report"
    _description = "Clearance Report"

    date_from = fields.Date(string="Date from", required=1)
    date_to = fields.Date(string="Date to", required=1)

    def print_states_report(self):
        """Print Clearance states report."""
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref("clearance_reports.clearance_states_report").report_action(
            self, data=data
        )

    def print_states_report_preview(self):
        """Print Clearance states report preview."""
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref(
            "clearance_reports.clearance_states_report_preview"
        ).report_action(self, data=data)

    def print_shipping_order_report(self):
        """Print Clearance states resume report."""
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref("clearance_reports.shipping_order_report").report_action(
            self, data=data
        )

    def print_shipping_order_report_preview(self):
        """Print Clearance states resume report preview."""
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref(
            "clearance_reports.shipping_order_report_preview"
        ).report_action(self, data=data)

    def print_cost_income_report(self):
        """Print Clearance states resume report."""
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref(
            "clearance_reports.clearance_payments_invoices_report"
        ).report_action(self, data=data)

    def print_cost_income_report_preview(self):
        """Print Clearance states resume report preview."""
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref(
            "clearance_reports.clearance_payments_invoices_report_preview"
        ).report_action(self, data=data)

    def print_transport_order_report(self):
        """Print Transport Order report."""
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref(
            "clearance_reports.clearance_transport_order_report"
        ).report_action(self, data=data)

    def print_transport_order_report_preview(self):
        """Print Transport Order report preview."""
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref(
            "clearance_reports.clearance_transport_order_report_preview"
        ).report_action(self, data=data)

    def print_warehouse_report(self):
        """Print Warehouse report."""
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref(
            "clearance_reports.clearance_warehouse_report"
        ).report_action(self, data=data)

    def name_get(self):
        res = []
        for report in self:
            res.append(
                (
                    report.id,
                    "{} - {} ".format(
                        report.date_from or "",
                        report.date_to or "",
                    ),
                )
            )
        return res


# ---------------------------
#  Report Clearance PDF
# ---------------------------


class ResumeClearanceReport(models.AbstractModel):
    _name = "report.clearance_reports.report_resume_clearance"
    _description = "Clearance Report Resume"

    def _get_lines(self, record):
        date_from = record.date_from
        date_to = record.date_to
        domain = [("date", "<=", date_to), ("date", ">=", date_from)]
        clearance = self.env["clearance.request"].search(domain, order="name asc")
        return clearance, [
            "draft",
            "customs_clearance",
            "customs_statement",
            "transport",
            "delivery",
            "delivery_done",
            "close",
        ]

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["clearance.report"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "clearance.report",
            "data": data,
            "docs": docs,
            "lang": self.env.user.lang,
            "get_lines": self._get_lines,
        }


class ResumeShippingReport(models.AbstractModel):
    _name = "report.clearance_reports.shipping_order_template"
    _description = "Shipping Orders Report Resume"

    def _get_lines(self, record):
        date_from = record.date_from
        date_to = record.date_to
        datetime_from = datetime.strptime(
            str(date_from) + " 00:00:00", "%Y-%m-%d %H:%M:%S"
        )
        datetime_to = datetime.strptime(str(date_to) + " 23:59:59", "%Y-%m-%d %H:%M:%S")
        domain_shipping = [
            ("create_date", ">=", datetime_from),
            ("create_date", "<=", datetime_to),
        ]
        shipping_orders = self.env["shipping.order"].search(
            domain_shipping, order="name asc"
        )
        return shipping_orders

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["clearance.report"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "clearance.report",
            "data": data,
            "docs": docs,
            "lang": self.env.user.lang,
            "get_lines": self._get_lines,
        }


class ResumeClearancePaymentsInvoices(models.AbstractModel):
    _name = "report.clearance_reports.clearance_payments_invoices_template"
    _description = "Clearance Costs and Incomes Report Resume"

    def _get_lines(self, record):
        date_from = record.date_from
        date_to = record.date_to
        domain = [("date", "<=", date_to), ("date", ">=", date_from)]
        clearance = self.env["clearance.request"].search(domain, order="name asc")
        return clearance

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["clearance.report"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "clearance.report",
            "data": data,
            "docs": docs,
            "lang": self.env.user.lang,
            "get_lines": self._get_lines,
        }


class TransportOrderReport(models.AbstractModel):
    _name = "report.clearance_reports.clearance_transport_order_template"
    _description = "Transport Order Report Resume"

    def _get_lines(self, record, request_type):
        tracking_lines = (
            self.env["mail.tracking.value"]
            .sudo()
            .search(
                [
                    ("mail_message_id.model", "=", "clearance.request"),
                    ("mail_message_id.date", ">=", record.date_from),
                    ("mail_message_id.date", "<=", record.date_to),
                    (
                        "old_value_char",
                        "in",
                        ["Customs Statement", "البيان الجمركي", "Draft", "مسودة"],
                    ),
                    ("new_value_char", "in", ["Transport", "نقل"]),
                ]
            )
        )
        # get clearances from tracking lines
        clearance_ids = tracking_lines.mapped("mail_message_id.res_id")
        clearance_data = self.env["clearance.request"].search(
            [("id", "in", clearance_ids), ("request_type", "=", request_type)]
        )
        return clearance_data

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["clearance.report"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "clearance.report",
            "data": data,
            "docs": docs,
            "lang": self.env.user.lang,
            "get_lines": self._get_lines,
        }


class ResumeClearanceWarehouse(models.AbstractModel):
    _name = "report.clearance_reports.clearance_warehouse_template"
    _description = "Clearance Warehouse Report Resume"

    def _get_lines(self, record):
        date_from = record.date_from
        date_to = record.date_to
        domain = [
            ("delivery_date", "<=", date_to),
            ("delivery_date", ">=", date_from),
            ("shipping_order_id.state", "!=", "canceled"),
        ]
        shipping_lines_warehouse = self.env["shipping.order.line"].search(
            [("shipping_order_id.transport_type", "=", "warehouse")] + domain
        )
        shipping_lines_customer = self.env["shipping.order.line"].search(
            [
                ("shipping_order_id.transport_type", "=", "customer"),
                ("shipping_order_id.shipping_order_id", "!=", False),
                (
                    "shipping_order_id.shipping_order_id",
                    "not in",
                    shipping_lines_warehouse.mapped("shipping_order_id").ids,
                ),
            ]
            + domain
        )
        shipping_lines = shipping_lines_customer + shipping_lines_warehouse
        return shipping_lines

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["clearance.report"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "clearance.report",
            "data": data,
            "docs": docs,
            "lang": self.env.user.lang,
            "get_lines": self._get_lines,
        }
