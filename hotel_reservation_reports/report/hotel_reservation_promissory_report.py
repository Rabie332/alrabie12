from odoo import api, fields, models


class HotelReservationPromissoryReport(models.TransientModel):
    _name = "hotel.reservation.promissory.report"
    _description = "Hotel Reservation promissory Report"

    date_from = fields.Date("From", required=True)
    date_to = fields.Date("To", required=True)
    user_id = fields.Many2one("res.users", string="User")
    partner_id = fields.Many2one(
        "res.partner", "Customer", domain="[('is_guest', '=', True)]"
    )
    state = fields.Selection(
        [("all", "All"), ("collected", "Collected"), ("no_collected", "No Collected")],
        default="all",
    )

    def name_get(self):
        result = []
        for record in self:
            name = "{}-{} ".format(record.date_from, record.date_to)
            result.append((record.id, name))
        return result

    def print_promissory_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return (
            self.with_context(promissory_type=self._context.get("partner_type"))
            .env.ref("hotel_reservation_reports.reservation_promissory_report_preview")
            .report_action(self, data=data)
        )


class ResumeHotelReservationPromissory(models.AbstractModel):
    _name = "report.hotel_reservation_reports.report_reservation_promissory"
    _description = "Hotel Reservation promissory Resume"

    def _get_lines(self, record):
        date_from = record.date_from
        date_to = record.date_to
        user_id = record.user_id
        partner_id = record.partner_id
        state = record.state
        domain = [
            ("date", "<=", date_to),
            ("date", ">=", date_from),
            ("reservation_id", "!=", False),
            ("state", "!=", "cancel"),
            (
                "support_type_id",
                "=",
                self.env.ref("hotel_reservation.payment_type_promissory").id,
            ),
        ]
        if state == "collected":
            domain.append(("state", "=", "posted"))
        if state == "no_collected":
            domain.append(("state", "!=", "posted"))
        if partner_id:
            domain.append(("partner_id", "=", partner_id))
        if user_id:
            domain.append(("create_uid", "=", user_id))
        payments = self.env["account.payment"].search(domain)
        return payments

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["hotel.reservation.promissory.report"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "hotel.reservation.promissory.report",
            "docs": docs,
            "lang": self.env.user.lang,
            "get_lines": self._get_lines,
        }
