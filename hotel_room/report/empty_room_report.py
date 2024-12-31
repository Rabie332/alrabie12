from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models


class EmptyRoomReport(models.AbstractModel):
    _name = "report.hotel_room.report_empty_room_template"
    _description = "Empty Rooms Report"

    def _get_lines(self, record):
        today = datetime.today().date()
        date_before_today = today - relativedelta(days=int(record.days))
        excluded_rooms = (
            self.env["hotel.room.reservation.line"]
            .search([])
            .filtered(
                lambda line: (
                    (
                        line.check_in.date() >= date_before_today
                        and line.check_in.date() <= today
                    )
                    or (
                        line.check_out.date() >= date_before_today
                        and line.check_out.date() <= today
                    )
                )
            )
            .mapped("room_id")
        )
        rooms = self.env["hotel.room"].search([("id", "not in", excluded_rooms.ids)])
        return rooms

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["empty.room.wizard"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "empty.room.wizard",
            "docs": docs,
            "get_lines": self._get_lines,
        }
