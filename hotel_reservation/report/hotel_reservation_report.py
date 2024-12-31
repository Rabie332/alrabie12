# See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ReportTestCheckin(models.AbstractModel):
    _name = "report.hotel_reservation.report_checkin_qweb"
    _description = "Auxiliar to get the check in report"

    def _get_checkin(self, data):
        date_start = datetime.strptime(data["date_start"], "%Y-%m-%d %H:%M:%S")
        date_end = datetime.strptime(data["date_end"], "%Y-%m-%d %H:%M:%S")
        reservations = (
            self.env["hotel.reservation"]
            .search([])
            .filtered(
                lambda reservation: (
                    reservation.rent == "hours"
                    and reservation.checkin >= date_start
                    and reservation.checkin <= date_end
                )
                or (
                    reservation.rent != "hours"
                    and reservation.checkin.date() >= date_start.date()
                    and reservation.checkin.date() <= date_end.date()
                )
            )
        )
        return reservations

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        data = data if data is not None else {}
        ids = data.get("ids", [])
        docs = self.env["hotel.reservation.wizard"].browse(ids)
        return {
            "doc_ids": docids,
            "doc_model": "hotel.reservation.wizard",
            "data": data,
            "docs": docs,
            "get_checkin": self._get_checkin,
        }


class ReportTestCheckout(models.AbstractModel):
    _name = "report.hotel_reservation.report_checkout_qweb"
    _description = "Auxiliar to get the check out report"

    def _get_checkout(self, data):
        date_start = datetime.strptime(data["date_start"], "%Y-%m-%d %H:%M:%S")
        date_end = datetime.strptime(data["date_end"], "%Y-%m-%d %H:%M:%S")
        # if the reservation is 'individual':
        # -  if rent 'hours' -> search by date time else search by date
        # -  filter reservation by date checkout if there is no date termination
        # -  filter reservation by date termination if there is date termination
        # if the reservation is 'collective':
        # -  if rent 'hours' -> search by date time else search by date
        # -  search reservation by date checkout if there is
        # no date termination and no date extension
        # -  search reservation by date termination if there is date termination
        # -  search reservation by date extensionif there is
        # no date termination and date extension

        reservation_lines = (
            self.env["hotel.reservation.line"]
            .search([])
            .filtered(
                lambda reservation_line: (
                    (
                        reservation_line.line_id.reservation_type == "individual"
                        and (
                            reservation_line.line_id.rent == "hours"
                            and (
                                (
                                    not reservation_line.line_id.date_termination
                                    and reservation_line.line_id.checkout >= date_start
                                    and reservation_line.line_id.checkout <= date_end
                                )
                                or (
                                    reservation_line.line_id.date_termination
                                    and reservation_line.line_id.date_termination
                                    >= date_start
                                    and reservation_line.line_id.date_termination
                                    <= date_end
                                )
                            )
                        )
                        or (
                            reservation_line.line_id.rent != "hours"
                            and (
                                (
                                    not reservation_line.line_id.date_termination
                                    and reservation_line.line_id.checkout
                                    and reservation_line.line_id.checkout.date()
                                    >= date_start.date()
                                    and reservation_line.line_id.checkout.date()
                                    <= date_end.date()
                                )
                                or (
                                    reservation_line.line_id.date_termination
                                    and reservation_line.line_id.date_termination.date()
                                    >= date_start.date()
                                    and reservation_line.line_id.date_termination.date()
                                    <= date_end.date()
                                )
                            )
                        )
                    )
                    or (
                        reservation_line.line_id.reservation_type == "collective"
                        and (
                            reservation_line.line_id.rent == "hours"
                            and (
                                (
                                    reservation_line.date_termination
                                    and reservation_line.date_termination >= date_start
                                    and reservation_line.date_termination <= date_end
                                )
                                or (
                                    not reservation_line.date_termination
                                    and reservation_line.date_extension
                                    and reservation_line.line_id.date_extension
                                    >= date_start
                                    and reservation_line.line_id.date_extension
                                    <= date_end
                                )
                                or (
                                    not reservation_line.date_termination
                                    and not reservation_line.date_extension
                                    and reservation_line.line_id.checkout >= date_start
                                    and reservation_line.line_id.checkout <= date_end
                                )
                            )
                            or reservation_line.line_id.rent != "hours"
                            and (
                                (
                                    reservation_line.date_termination
                                    and reservation_line.date_termination.date()
                                    >= date_start.date()
                                    and reservation_line.date_termination.date()
                                    <= date_end.date()
                                )
                                or (
                                    not reservation_line.date_termination
                                    and reservation_line.date_extension
                                    and reservation_line.line_id.date_extension.date()
                                    >= date_start.date()
                                    and reservation_line.line_id.date_extension.date()
                                    <= date_end.date()
                                )
                                or (
                                    not reservation_line.date_termination
                                    and not reservation_line.date_extension
                                    and reservation_line.line_id.checkout.date()
                                    >= date_start.date()
                                    and reservation_line.line_id.checkout.date()
                                    <= date_end.date()
                                )
                            )
                        )
                    )
                )
            )
        )
        return reservation_lines

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        data = data if data is not None else {}
        ids = data.get("ids", [])
        docs = self.env["hotel.reservation.wizard"].browse(ids)
        return {
            "doc_ids": docids,
            "doc_model": "hotel.reservation.wizard",
            "data": data,
            "docs": docs,
            "get_checkout": self._get_checkout,
        }


class ReportTestMaxroom(models.AbstractModel):
    _name = "report.hotel_reservation.report_maxroom_qweb"
    _description = "Auxiliar to get the room report"

    def _get_data(self, data):
        date_start = datetime.strptime(data["date_start"], "%Y-%m-%d %H:%M:%S")
        date_end = datetime.strptime(data["date_end"], "%Y-%m-%d %H:%M:%S")
        reservations = (
            self.env["hotel.reservation"]
            .search([])
            .filtered(
                lambda reservation: (
                    reservation.rent == "hours"
                    and reservation.checkin >= date_start
                    and reservation.checkout <= date_end
                )
                or (
                    reservation.rent != "hours"
                    and reservation.checkin.date() >= date_start.date()
                    and reservation.checkout.date() <= date_end.date()
                )
            )
        )
        return reservations

    def _get_room_used_detail(self, data):
        room_used_details = []
        date_start = data["date_start"]
        date_end = data["date_end"]
        hotel_room_obj = self.env["hotel.room"]
        for room in hotel_room_obj.search([]):
            counter = 0
            details = {}
            if room.room_reservation_line_ids:
                end_date = datetime.strptime(date_end, DEFAULT_SERVER_DATETIME_FORMAT)
                start_date = datetime.strptime(
                    date_start, DEFAULT_SERVER_DATETIME_FORMAT
                )
                counter = len(
                    room.room_reservation_line_ids.filtered(
                        lambda l: start_date.date()
                        <= l.check_in.date()
                        <= end_date.date()
                    )
                )
            if counter >= 1:
                details.update({"name": room.name or "", "no_of_times_used": counter})
                room_used_details.append(details)
        return room_used_details

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        data = data if data is not None else {}
        ids = data.get("ids", [])
        docs = self.env["hotel.reservation.wizard"].browse(ids)
        return {
            "doc_ids": docids,
            "doc_model": "hotel.reservation.wizard",
            "data": data,
            "docs": docs,
            "get_data": self._get_data,
            "get_room_used_detail": self._get_room_used_detail,
        }


class ReportRoomReservation(models.AbstractModel):
    _name = "report.hotel_reservation.report_room_reservation_qweb"
    _description = "Auxiliar to get the room report"

    def _get_data(self, data):
        date_start = datetime.strptime(data["date_start"], "%Y-%m-%d %H:%M:%S")
        date_end = datetime.strptime(data["date_end"], "%Y-%m-%d %H:%M:%S")
        reservations = (
            self.env["hotel.reservation"]
            .search([])
            .filtered(
                lambda reservation: (
                    reservation.rent == "hours"
                    and reservation.checkin >= date_start
                    and reservation.checkout <= date_end
                )
                or (
                    reservation.rent != "hours"
                    and reservation.checkin.date() >= date_start.date()
                    and reservation.checkout.date() <= date_end.date()
                )
            )
        )
        return reservations

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        data = data if data is not None else {}
        ids = data.get("ids", [])
        docs = self.env["hotel.reservation.wizard"].browse(ids)
        return {
            "doc_ids": docids,
            "doc_model": "hotel.reservation.wizard",
            "data": data,
            "docs": docs,
            "get_data": self._get_data,
        }
