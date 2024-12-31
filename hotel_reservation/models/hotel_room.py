# See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
# open_reservation_action
_logger = logging.getLogger(__name__)
try:
    import pytz
except (ImportError, IOError) as err:
    _logger.debug(err)


class HotelRoom(models.Model):

    _inherit = "hotel.room"
    _description = "Hotel Room"

    room_reservation_line_ids = fields.One2many(
        "hotel.room.reservation.line", "room_id", string="Room Reserve Line"
    )
    to_checked_in = fields.Boolean(
        compute="_compute_to_checked_in", search="_search_to_checked_in"
    )
    to_exit_today = fields.Boolean(
        compute="_compute_to_exit_today", search="_search_to_exit_today"
    )
    waiting_check_in = fields.Boolean(
        compute="_compute_waiting_check_in", search="_search_waiting_check_in"
    )
    waiting_checkin_to_reserve = fields.Boolean(
        compute="_compute_waiting_checkin_to_reserve",
        search="_search_waiting_checkin_to_reserve",
    )

    to_extend = fields.Boolean(
        compute="_compute_to_extend",
    )
    is_hospitality = fields.Boolean(compute="_compute_is_hospitality", store=1)
    bg_color = fields.Char(compute="_compute_colors", store=1)
    kanban_color = fields.Char(compute="_compute_colors", store=1)

    @api.depends(
        "status",
        "is_clean",
        "to_extend",
        "to_exit_today",
        "to_checked_in",
        "is_hospitality",
    )
    def _compute_colors(self):
        """Calculate kanan colors"""
        for room in self:
            room.bg_color = room.kanban_color = ""
            if room.status == "occupied":
                room.bg_color = "#FF1F36"
            elif room.status == "available" and room.is_clean:
                room.bg_color = "#4AC571"
            elif room.status == "available" and not room.is_clean:
                room.bg_color = "#FF8A34"
            elif room.status == "maintenance":
                room.bg_color = "#D2D1D1"
            if room.is_hospitality:
                room.bg_color = "#d4af37"
            if room.to_checked_in:
                room.kanban_color = "oe_kanban_color_10"
            elif room.to_extend or room.to_exit_today:
                room.kanban_color = "oe_kanban_color_4"

    def _search_to_checked_in(self, operator, value):
        """Search Rooms to check in"""
        reservations = (
            self.env["hotel.room"]
            .search([])
            .mapped("room_reservation_line_ids.reservation_id")
            .filtered(
                lambda reservation: reservation.display_button_check_in_reservation
            )
        )
        rooms = []
        for reservation in reservations:
            # Search room if it's individual
            if reservation.reservation_type == "individual":
                rooms += reservation.reservation_line.mapped("room_id").ids
            else:
                # Search room if it's collective
                # - reservation haven't date check out
                # - date termination of reservation  equal or greater of today
                # - date check out  of reservation should be equal or greater
                # of today (if there is no date termination and no date extension)
                # - date extension of reservation should be equal or greater
                # of today (if there is no date termination)
                # if reservation is hourly check by date time else check by date
                rooms += (
                    reservation.reservation_line.filtered(
                        lambda line: not line.date_check_in
                    )
                    .mapped("room_id")
                    .ids
                )

        return [("id", "in", rooms)]

    def get_reservation_to_checked_in(self):
        """Get Reservation to check out"""
        reservations = []
        for reservation in self.room_reservation_line_ids.mapped(
            "reservation_id"
        ).filtered(lambda reservation: reservation.display_button_check_in_reservation):
            if (
                reservation.reservation_type == "individual"
                and self.id in reservation.reservation_line.mapped("room_id").ids
            ) or (
                reservation.reservation_type == "collective"
                and reservation.reservation_line.filtered(
                    lambda line: not line.date_check_in and line.room_id == self
                )
            ):
                reservations.append(reservation.id)
        return reservations

    def get_reservation_to_extend(self):
        """Get Reservation to extend"""
        reservations = []
        for reservation in self.room_reservation_line_ids.mapped(
            "reservation_id"
        ).filtered(lambda reservation: reservation.display_button_extend_reservation):
            if reservation.reservation_type == "individual" or (
                reservation.reservation_type == "collective"
                and reservation.reservation_line.filtered(
                    lambda line: line.room_id == self
                    and not reservation.date_check_out
                    and not reservation.date_termination
                )
            ):
                reservations.append(reservation.id)
        return reservations

    def _compute_to_checked_in(self):
        """Calculate check in"""
        for room in self:
            room.to_checked_in = False
            if room.get_reservation_to_checked_in():
                room.to_checked_in = True

    def _compute_to_extend(self):
        """Calculate to extend"""
        for room in self:
            room.to_extend = False
            if room.get_reservation_to_extend():
                room.to_extend = True
    @api.depends(
        "room_reservation_line_ids",
        "room_reservation_line_ids.reservation_id",
        "room_reservation_line_ids.reservation_id.is_hospitality",
        "room_reservation_line_ids.reservation_id.state",
    )
    def _compute_is_hospitality(self):
        """Calculate is_hospitality"""
        for room in self:
            room.is_hospitality = False
            today = datetime.today().date()
            reservations_is_hospitality = room.room_reservation_line_ids.filtered(
                lambda reservation: reservation.check_in.date()
                <= today
                <= reservation.check_out.date()
                and reservation.state != "cancel"
                and reservation.reservation_id.is_hospitality
            )
            if reservations_is_hospitality:
                room.is_hospitality = True

    def get_reservation_to_check_out(self):
        """Get reservation to check out"""
        reservations = []
        for reservation in self.room_reservation_line_ids.mapped(
            "reservation_id"
        ).filtered(
            lambda reservation: reservation.display_button_check_out_reservation
        ):
            # Search reservation if it's collective
            # - reservation have check in and haven't checkout
            # - today should  equal or greater of date termination of reservation
            # - today should be equal or greater of date check out
            # (if there is no date termination and no date extension)
            # - today should be equal or greater of date extension
            # of reservation (if there is no date termination)
            # if reservation is hourly check by date time else check by date
            if reservation.reservation_type == "individual" or (
                reservation.reservation_type == "collective"
                and reservation.reservation_line.filtered(
                    lambda line: not line.date_check_out
                    and line.date_check_in
                    and not line.date_check_out
                    and line.room_id == self
                    and (
                        (
                            reservation.rent != "hours"
                            and (
                                (
                                    line.date_termination
                                    and datetime.today().date()
                                    >= line.date_termination.date()
                                )
                                or (
                                    not line.date_termination
                                    and (
                                        (
                                            reservation.checkout.date()
                                            <= datetime.today().date()
                                            and not line.date_extension
                                        )
                                        or (
                                            line.date_extension
                                            and line.date_extension.date()
                                            <= datetime.today().date()
                                        )
                                    )
                                )
                            )
                        )
                        or (
                            reservation.rent == "hours"
                            and (
                                (
                                    line.date_termination
                                    and datetime.today() >= line.date_termination
                                )
                                or (
                                    not line.date_termination
                                    and (
                                        (
                                            reservation.checkout <= datetime.today()
                                            and not line.date_extension
                                        )
                                        or (
                                            line.date_extension
                                            and line.date_extension <= datetime.today()
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            ):
                reservations.append(reservation.id)
        return reservations

    def _search_to_exit_today(self, operator, value):
        """Search rooms to check out"""
        reservations = (
            self.env["hotel.room"]
            .search([])
            .mapped("room_reservation_line_ids.reservation_id")
            .filtered(
                lambda reservation: reservation.display_button_check_out_reservation
            )
        )
        rooms = []
        for reservation in reservations:
            # if reservation is individual
            if reservation.reservation_type == "individual":
                rooms += reservation.reservation_line.mapped("room_id").ids
            else:
                # if reservation is collective
                # - reservation have check in and haven't checkout
                # - today should  equal or greater of date termination of reservation
                # - today should be equal or greater of date check out
                # (if there is no date termination and no date extension)
                # - today should be equal or greater of date extension
                # of reservation (if there is no date termination)
                # if reservation is hourly check by date time else check by date
                rooms += (
                    reservation.reservation_line.filtered(
                        lambda line: not line.date_check_out
                        and line.date_check_in
                        and (
                            (
                                reservation.rent != "hours"
                                and (
                                    (
                                        line.date_termination
                                        and datetime.today().date()
                                        >= line.date_termination.date()
                                    )
                                    or (
                                        not line.date_termination
                                        and (
                                            (
                                                reservation.checkout.date()
                                                <= datetime.today().date()
                                                and not line.date_extension
                                            )
                                            or (
                                                line.date_extension
                                                and line.date_extension.date()
                                                <= datetime.today().date()
                                            )
                                        )
                                    )
                                )
                            )
                            or (
                                reservation.rent == "hours"
                                and (
                                    (
                                        line.date_termination
                                        and datetime.today() >= line.date_termination
                                    )
                                    or (
                                        not line.date_termination
                                        and (
                                            (
                                                reservation.checkout <= datetime.today()
                                                and not line.date_extension
                                            )
                                            or (
                                                line.date_extension
                                                and line.date_extension
                                                <= datetime.today()
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                    .mapped("room_id")
                    .ids
                )

        return [("id", "in", rooms)]

    def _compute_to_exit_today(self):
        """Get room check out"""
        for room in self:
            room.to_exit_today = False
            if room.get_reservation_to_check_out():
                room.to_exit_today = True

    def _search_waiting_check_in(self, operator, value):
        """seach rooms to check in"""
        domain = self._search_to_checked_in(operator, value)
        rooms = [] + self.search(domain).ids
        for room in self.search([]):
            reservations = room.get_waiting_check_in()
            if reservations:
                rooms.append(room.id)
        return [("id", "in", rooms)]

    def get_waiting_check_in(self):
        """Get rooms waiting to check in"""
        reservations = []
        # get reservation confirmed and without date check in
        # - date check in and check out should be between today
        reservations += (
            self.room_reservation_line_ids.filtered(
                lambda line: line.reservation_id.state in ("confirm", "done")
                and (
                    (
                        line.reservation_id.reservation_type == "individual"
                        and not line.reservation_id.date_check_in
                    )
                    or (
                        line.reservation_id.reservation_type == "collective"
                        and line.reservation_line_id.room_id == self
                        and not line.reservation_line_id.date_check_in
                    )
                )
                and (
                    fields.Datetime.now().date()
                    <= line.check_in.date()
                    <= fields.Datetime.now().date()
                    or (
                        fields.Datetime.now().date()
                        <= line.check_out.date()
                        <= fields.Datetime.now().date()
                    )
                    or (
                        line.check_in.date() <= fields.Datetime.now().date()
                        and line.check_out.date() >= fields.Datetime.now().date()
                    )
                )
            )
            .mapped("reservation_id")
            .ids
        )
        # get reservation draft
        # - date check in and check out should be between today
        reservations += (
            self.env["hotel.reservation.line"]
            .search([("room_id", "=", self.id)])
            .mapped("line_id")
            .filtered(
                lambda line_reservation: line_reservation.state == "draft"
                and (
                    fields.Datetime.now().date()
                    <= line_reservation.checkin.date()
                    <= fields.Datetime.now().date()
                    or (
                        fields.Datetime.now().date()
                        <= line_reservation.checkout.date()
                        <= fields.Datetime.now().date()
                    )
                    or (
                        line_reservation.checkin.date() <= fields.Datetime.now().date()
                        and line_reservation.checkout.date()
                        >= fields.Datetime.now().date()
                    )
                )
            )
            .ids
        )
        return reservations

    def _compute_waiting_check_in(self):
        """Calculate waiting check in"""
        for room in self:
            room.waiting_check_in = False
            reservations = room.get_waiting_check_in()
            if reservations or room.get_reservation_to_checked_in():
                room.waiting_check_in = True

    def get_waiting_checkin_to_reserve(self):
        """Get rooms waiting to check in and reserve"""
        display_create_reservation = True
        # get rooms that is reserved in this days. we c'ant create reservation in this day
        # - reservation in state ("confirm", "done")
        # - reservation and haven't  date_check_out
        # - date check in and check out should be between today
        if self.room_reservation_line_ids.filtered(
            lambda line: line.reservation_id.state in ("confirm", "done")
            and (
                (
                    line.reservation_id.reservation_type == "individual"
                    and not line.reservation_id.date_check_out
                    and line.reservation_id.date_check_in
                )
                or (
                    line.reservation_id.reservation_type == "collective"
                    and line.reservation_line_id.room_id == self
                    and not line.reservation_line_id.date_check_out
                    and not line.reservation_line_id.date_check_in
                )
            )
            and (
                fields.Datetime.now().date()
                <= line.check_in.date()
                <= fields.Datetime.now().date()
                or (
                    fields.Datetime.now().date()
                    <= line.check_out.date()
                    <= fields.Datetime.now().date()
                )
                or (
                    line.check_in.date() <= fields.Datetime.now().date()
                    and line.check_out.date() >= fields.Datetime.now().date()
                )
            )
        ):
            display_create_reservation = False
        return display_create_reservation

    def _search_waiting_checkin_to_reserve(self, operator, value):
        """seach rooms to check in and waiting and that don't have reserve today"""
        domain = self._search_waiting_check_in(operator, value)
        rooms = [] + self.search(domain).ids
        for room in self.search([]):
            reservations = room.get_waiting_checkin_to_reserve()
            if reservations:
                rooms.append(room.id)
        return [("id", "in", rooms)]

    def _compute_waiting_checkin_to_reserve(self):
        """Calculate waiting check in and to reserve"""
        for room in self:
            room.waiting_checkin_to_reserve = False
            if (
                room.get_waiting_check_in()
                or room.get_reservation_to_checked_in()
                or room.get_waiting_checkin_to_reserve()
            ):
                room.waiting_checkin_to_reserve = True

    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        for room in self:
            for reserv_line in room.room_reservation_line_ids:
                if reserv_line.status == "confirm":
                    raise ValidationError(
                        _(
                            """User is not able to delete the """
                            """room after the room in %s state """
                            """in reservation"""
                        )
                        % (reserv_line.status)
                    )
        return super(HotelRoom, self).unlink()

    def open_reservation_action(self):
        is_from_check_in = self.env.context.get("is_from_check_in")
        is_from_check_out = self.env.context.get("is_from_check_out")
        context = {}
        res_id = False
        line_ids = self.env["hotel.reservation.line"].search(
            [("room_id", "in", [self.id])]
        )
        is_form = False
        reservation_ids = False
        domain = []
        if is_from_check_in:
            reservation_ids = self.get_reservation_to_checked_in()
            if not reservation_ids:
                reservation_ids = self.get_waiting_check_in()
            is_form = True
        if is_from_check_out:
            reservation_ids = self.get_reservation_to_check_out()
            is_form = True
        else:
            all_reservation_ids = line_ids.mapped("line_id")
        if not is_form:
            domain = [("id", "in", all_reservation_ids.ids)]
        if reservation_ids:
            res_id = reservation_ids[-1]
        else:
            line = self.env["hotel.reservation.line"].create({"room_id": self.id})
            context = dict(
                self.env.context,
                default_checkin=fields.Datetime.now(),
                # default_duration=1,
                # default_checkout=fields.Datetime.now(),
                default_reservation_line=[(6, 0, [line.id])],
            )
        return {
            "name": _("Reservation"),
            "type": "ir.actions.act_window",
            "view_mode": "form" if is_form else "tree,form",
            "res_model": "hotel.reservation",
            "res_id": res_id,
            "domain": domain,
            "context": context,
        }

    def get_status_room_dates(self, reservation, checkin, checkout):
        """Get room status"""
        is_status_occupied = False
        for reservation_line in self.room_reservation_line_ids.search(
            [
                ("status", "in", ("confirm", "done", "finish")),
                ("room_id", "=", self.id),
                ("reservation_id", "!=", reservation._origin.id),
            ]
        ):
            check_in = reservation_line.check_in
            check_out = reservation_line.check_out

            if (
                not reservation_line.reservation_id.date_check_out
                and reservation_line.reservation_id.reservation_type == "individual"
            ) or (
                not reservation_line.reservation_line_id.date_check_out
                and reservation_line.reservation_line_id.room_id
                == reservation_line.room_id
                and reservation_line.reservation_id.reservation_type == "collective"
            ):
                if (
                    (
                        check_in.date()
                        and checkin.date()
                        and checkout
                        and check_out.date()
                    )
                    and (check_in <= checkin <= check_out)
                    or (check_in.date() <= checkout.date() <= check_out.date())
                    or (
                        checkin.date() <= check_in.date()
                        and checkout.date() >= check_out.date()
                    )
                ):
                    is_status_occupied = True
        return is_status_occupied

    def apartment_check_in(self):
        rooms = self.env["hotel.room"].sudo().search([("to_checked_in", "=", True)])
        domain = [("id", "in", rooms.ids)]
        apartment_kanban = self.env.ref("hotel_reservation.apartment_view_kanban")
        context = dict(
            is_from_check_in=True,
        )
        return {
            "name": _("Check In"),
            "type": "ir.actions.act_window",
            "view_mode": "kanban",
            "views": [(apartment_kanban.id, "kanban")],
            "res_model": "hotel.room",
            "domain": domain,
            "context": context,
        }

    def apartment_check_out(self):
        room_ids = self.env["hotel.room"].search([("to_exit_today", "=", True)])
        domain = [("id", "in", room_ids.ids)]
        apartment_kanban = self.env.ref("hotel_reservation.apartment_view_kanban")
        context = dict(
            is_from_check_out=True,
        )
        return {
            "name": _("Check Out"),
            "type": "ir.actions.act_window",
            "view_mode": "kanban",
            "views": [(apartment_kanban.id, "kanban")],
            "res_model": "hotel.room",
            "domain": domain,
            "context": context,
        }


class RoomReservationSummary(models.Model):

    _name = "room.reservation.summary"
    _description = "Room reservation summary"

    name = fields.Char("Reservation Summary", default="Reservations Summary")
    date_from = fields.Datetime("Date From", default=lambda self: fields.Date.today())
    date_to = fields.Datetime(
        "Date To",
        default=lambda self: fields.Date.today() + relativedelta(days=30),
    )
    summary_header = fields.Text("Summary Header")
    room_summary = fields.Text("Room Summary")

    def room_reservation(self):
        """
        @param self: object pointer
        """
        resource_id = self.env.ref("hotel_reservation.view_hotel_reservation_form").id
        return {
            "name": _("Reconcile Write-Off"),
            "context": self._context,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "hotel.reservation",
            "views": [(resource_id, "form")],
            "type": "ir.actions.act_window",
            "target": "new",
        }

    @api.onchange("date_from", "date_to")  # noqa C901 (function is too complex)
    def get_room_summary(self):  # noqa C901 (function is too complex)
        """
        @param self: object pointer
        """
        res = {}
        all_detail = []
        room_obj = self.env["hotel.room"]
        reservation_line_obj = self.env["hotel.room.reservation.line"]
        folio_room_line_obj = self.env["folio.room.line"]
        user_obj = self.env["res.users"]
        date_range_list = []
        main_header = []
        summary_header_list = ["Rooms"]
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise UserError(_("Checkout date should be greater than Checkin date."))
            if self._context.get("tz", False):
                timezone = pytz.timezone(self._context.get("tz", False))
            else:
                timezone = pytz.timezone("UTC")
            d_frm_obj = (
                (self.date_from)
                .replace(tzinfo=pytz.timezone("UTC"))
                .astimezone(timezone)
            )
            d_to_obj = (
                (self.date_to).replace(tzinfo=pytz.timezone("UTC")).astimezone(timezone)
            )
            temp_date = d_frm_obj
            while temp_date <= d_to_obj:
                val = ""
                val = (
                    str(temp_date.strftime("%a"))
                    + " "
                    + str(temp_date.strftime("%b"))
                    + " "
                    + str(temp_date.strftime("%d"))
                )
                summary_header_list.append(val)
                date_range_list.append(temp_date.strftime(dt))
                temp_date = temp_date + timedelta(days=1)
            all_detail.append(summary_header_list)
            room_ids = room_obj.search([])
            all_room_detail = []
            for room in room_ids:
                room_detail = {}
                room_list_stats = []
                room_detail.update({"name": room.name or ""})
                if not room.room_reservation_line_ids and not room.room_line_ids:
                    for chk_date in date_range_list:
                        room_list_stats.append(
                            {"state": "Free", "date": chk_date, "room_id": room.id}
                        )
                else:
                    for chk_date in date_range_list:
                        ch_dt = chk_date[:10] + " 23:59:59"
                        ttime = datetime.strptime(ch_dt, dt)
                        c = ttime.replace(tzinfo=timezone).astimezone(
                            pytz.timezone("UTC")
                        )
                        chk_date = c.strftime(dt)
                        reserline_ids = room.room_reservation_line_ids.ids
                        reservline_ids = reservation_line_obj.search(
                            [
                                ("id", "in", reserline_ids),
                                ("check_in", "<=", chk_date),
                                ("check_out", ">=", chk_date),
                                ("state", "=", "assigned"),
                            ]
                        )
                        if not reservline_ids:
                            sdt = dt
                            chk_date = datetime.strptime(chk_date, sdt)
                            chk_date = datetime.strftime(
                                chk_date - timedelta(days=1), sdt
                            )
                            reservline_ids = reservation_line_obj.search(
                                [
                                    ("id", "in", reserline_ids),
                                    ("check_in", "<=", chk_date),
                                    ("check_out", ">=", chk_date),
                                    ("state", "=", "assigned"),
                                ]
                            )
                            for res_room in reservline_ids:
                                cid = res_room.check_in
                                cod = res_room.check_out
                                dur = cod - cid
                                if room_list_stats:
                                    count = 0
                                    for rlist in room_list_stats:
                                        cidst = datetime.strftime(cid, dt)
                                        codst = datetime.strftime(cod, dt)
                                        rm_id = res_room.room_id.id
                                        ci = rlist.get("date") >= cidst
                                        co = rlist.get("date") <= codst
                                        rm = rlist.get("room_id") == rm_id
                                        st = rlist.get("state") == "Reserved"
                                        if ci and co and rm and st:
                                            count += 1
                                    if count - dur.days == 0:
                                        c_id1 = user_obj.browse(self._uid)
                                        c_id = c_id1.company_id
                                        con_add = 0
                                        amin = 0.0
                                        # When configured_addition_hours is
                                        # greater than zero then we calculate
                                        # additional minutes
                                        if c_id:
                                            con_add = c_id.additional_hours
                                        if con_add > 0:
                                            amin = abs(con_add * 60)
                                        hr_dur = abs(dur.seconds / 60)
                                        if amin > 0:
                                            # When additional minutes is greater
                                            # than zero then check duration with
                                            # extra minutes and give the room
                                            # reservation status is reserved
                                            # --------------------------
                                            if hr_dur >= amin:
                                                reservline_ids = True
                                            else:
                                                reservline_ids = False
                                        else:
                                            if hr_dur > 0:
                                                reservline_ids = True
                                            else:
                                                reservline_ids = False
                                    else:
                                        reservline_ids = False
                        fol_room_line_ids = room.room_line_ids.ids
                        chk_state = ["draft", "cancel"]
                        folio_resrv_ids = folio_room_line_obj.search(
                            [
                                ("id", "in", fol_room_line_ids),
                                ("check_in", "<=", chk_date),
                                ("check_out", ">=", chk_date),
                                ("status", "not in", chk_state),
                            ]
                        )
                        if reservline_ids or folio_resrv_ids:
                            room_list_stats.append(
                                {
                                    "state": "Reserved",
                                    "date": chk_date,
                                    "room_id": room.id,
                                    "is_draft": "No",
                                    "data_model": "",
                                    "data_id": 0,
                                }
                            )
                        else:
                            room_list_stats.append(
                                {"state": "Free", "date": chk_date, "room_id": room.id}
                            )

                room_detail.update({"value": room_list_stats})
                all_room_detail.append(room_detail)
            main_header.append({"header": summary_header_list})
            self.summary_header = str(main_header)
            self.room_summary = str(all_room_detail)
        return res
