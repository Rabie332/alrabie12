import datetime
import json
import logging
import math

import pytz
import requests
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.base.models.res_partner import _tz_get

_logger = logging.getLogger(__name__)


class HrAttendanceBiotime(models.Model):
    _name = "hr.attendance.biotime"
    _description = "Attendance Biotime"

    name = fields.Char(string="URL", required=True)
    port_no = fields.Integer(string="Port", required=True, default=8084)
    active = fields.Boolean(default=True)
    last_transaction_date = fields.Datetime(
        string="Last updated date", default=fields.datetime.now()
    )
    biotime_tz = fields.Selection(_tz_get, string="Biotime Timezone", required=True)
    forgive_no_check_out = fields.Boolean(
        string="Forgive forgetting to check out", default=True
    )

    def float_time_convert_str(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        hour = factor * int(math.floor(val))
        minute = int((val % 1) * 60)
        return "{}:{}".format(str(hour).zfill(2), str(minute).zfill(2))

    def _date_to_utc(self, naive_dt):
        naive = datetime.datetime.strptime(naive_dt, "%Y-%m-%d %H:%M:%S")
        biotime_tz = pytz.timezone(self.biotime_tz)
        local_dt = biotime_tz.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        utc_dt_str = str(utc_dt)
        date = datetime.datetime.strptime(
            utc_dt_str.replace("+00:00", ""), "%Y-%m-%d %H:%M:%S"
        )
        return date

    def _date_to_local(self, naive_dt):
        naive = datetime.datetime.strptime(naive_dt, "%Y-%m-%d %H:%M:%S")
        biotime_tz = pytz.timezone(self.biotime_tz)
        ran = pytz.utc.localize(naive).astimezone(biotime_tz)
        date = datetime.datetime.strptime(str(ran)[:19], "%Y-%m-%d %H:%M:%S")
        return date

    def close_last_attendance_yesterday(self, employee_id, date):
        # get last attendance of yesterday
        attendance_yesterday_date = (date - relativedelta(days=1)).strftime("%Y-%m-%d")
        last_attendance_yesterday = self.env["hr.attendance"].search(
            [
                ("employee_id", "=", employee_id.id),
                (
                    "check_in",
                    "<=",
                    datetime.datetime.strptime(
                        attendance_yesterday_date + " 23:59:59", "%Y-%m-%d %H:%M:%S"
                    ),
                ),
                ("check_out", "=", False),
            ],
            order="check_in desc",
            limit=1,
        )
        # if check_out of last attendance is empty then set it by time check out
        # of working hours of current employee according to current date.
        # if the current employee hasn't calendar attendance
        # for this day close check out by check in.
        if last_attendance_yesterday and not last_attendance_yesterday.check_out:
            if self.forgive_no_check_out:
                resource_calendar_attendance = self.env[
                    "resource.calendar.attendance"
                ].search(
                    [
                        ("calendar_id", "=", employee_id.resource_calendar_id.id),
                        (
                            "dayofweek",
                            "=",
                            str(last_attendance_yesterday.check_in.weekday()),
                        ),
                    ],
                    order="hour_from desc",
                    limit=1,
                )
                if resource_calendar_attendance:
                    str_date_check_out = (
                        last_attendance_yesterday.check_in.strftime("%Y-%m-%d")
                        + " "
                        + self.float_time_convert_str(
                            resource_calendar_attendance.hour_to
                        )
                    )
                    check_out = datetime.datetime.strptime(
                        str_date_check_out, "%Y-%m-%d %H:%M"
                    )
                    # if check_out of calendar attendance less than check in
                    # of attendance then close it by time check in.
                    if check_out < last_attendance_yesterday.check_in:
                        last_attendance_yesterday.check_out = (
                            last_attendance_yesterday.check_in
                        )
                    else:
                        last_attendance_yesterday.check_out = check_out
                else:
                    last_attendance_yesterday.check_out = (
                        last_attendance_yesterday.check_in
                    )
            else:
                last_attendance_yesterday.check_out = last_attendance_yesterday.check_in

    @api.model
    def cron_download(self):
        """Call download_attendance method for all Biotime machine."""
        biotimes = self.env["hr.attendance.biotime"].search([])
        for biotime in biotimes:
            biotime.download_attendance()

    def download_attendance(self):
        for rec in self:
            biotime_token = (
                self.env["ir.config_parameter"].sudo().get_param("biotime_token", "")
            )
            try:
                biotime_url = f"{rec.name}:{rec.port_no}"
                if not biotime_token:
                    biotime_token = self._get_biotime_token(biotime_url)
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Token " + biotime_token,
                }
                transactions_endpiont = (
                    biotime_url + "/iclock/api/transactions/?page_size=1000000"
                )
                # flake8: noqa: B950
                if rec.last_transaction_date:
                    # Convert date_time to local time zone
                    last_transaction_date = self._date_to_local(
                        rec.last_transaction_date.strftime("%Y-%m-%d %H:%M:%S")
                    )
                    transactions_endpiont = f"{biotime_url}/iclock/api/transactions/?page_size=1000000&start_time={last_transaction_date}"
                transactions_response = requests.get(
                    transactions_endpiont, headers=headers
                )
            except Exception:
                raise ValidationError(_("Biotime is not available."))
            attendances = json.loads(transactions_response.content).get("data")
            attendances.sort(key=lambda attendance: attendance.get("punch_time"))
            for attendance in attendances:
                # prepare date of attendance
                employee = (
                    self.env["hr.employee"]
                    .sudo()
                    .search([("fingerprint_code", "=", attendance.get("emp_code"))])
                )
                if employee:
                    punch_time = self._date_to_utc(attendance.get("punch_time"))
                    # get last attendance for current day
                    attendance_date = punch_time.strftime("%Y-%m-%d")
                    last_attendance = self.env["hr.attendance"].search(
                        [
                            ("employee_id", "=", employee.id),
                            (
                                "check_in",
                                ">=",
                                datetime.datetime.strptime(
                                    attendance_date + " 00:00:00", "%Y-%m-%d %H:%M:%S"
                                ),
                            ),
                            (
                                "check_in",
                                "<=",
                                datetime.datetime.strptime(
                                    attendance_date + " 23:59:59", "%Y-%m-%d %H:%M:%S"
                                ),
                            ),
                        ],
                        order="check_in desc",
                        limit=1,
                    )
                    if not last_attendance:
                        # close attendance of yesterday.
                        self.close_last_attendance_yesterday(employee, punch_time)
                    self.sync_employee_attendance(employee, punch_time)
            rec.last_transaction_date = datetime.datetime.now()

    def sync_employee_attendance(self, employee, date):
        checkin_start = datetime.datetime.strptime(
            str(date), "%Y-%m-%d %H:%M:%S"
        ).date()
        checkin_start = str(checkin_start) + " 00:00:00"
        checkin_end = datetime.datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S").date()
        checkin_end = str(checkin_end) + " 23:59:59"
        emp_attendance = (
            self.env["hr.attendance"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", employee.id),
                    ("check_in", ">=", checkin_start),
                    ("check_in", "<=", checkin_end),
                ],
                limit=1,
                order="check_in desc",
            )
        )
        # if employee have another checkIn so change set check_out
        if emp_attendance:
            # check if (date) == check_in or  == check_out, if true do nothing
            if date != emp_attendance.check_in and date != emp_attendance.check_out:
                if not emp_attendance.check_out:
                    if emp_attendance.check_in > date:
                        emp_attendance.check_out = emp_attendance.check_in
                        emp_attendance.check_in = date
                    else:
                        emp_attendance.check_out = date
                    employee.attendance_state = "checked_out"
                else:
                    if date < emp_attendance.check_in:
                        # make checkout as checkIn in new record
                        vals = {
                            "employee_id": employee.id,
                            "check_in": emp_attendance.check_out,
                        }
                        self.env["hr.attendance"].sudo().create(vals)
                        employee.attendance_state = "checked_in"

                        # Make the checkIn as checkOut and date is checkIn
                        emp_attendance.check_out = emp_attendance.check_in
                        emp_attendance.check_in = date
                    elif (
                        date > emp_attendance.check_in
                        and date < emp_attendance.check_out
                    ):
                        # make checkOut as checkIn in new record,
                        # then make date as the checkout of current record
                        vals = {
                            "employee_id": employee.id,
                            "check_in": emp_attendance.check_out,
                        }
                        self.env["hr.attendance"].sudo().create(vals)
                        employee.attendance_state = "checked_in"

                        # then make the checkin as checkout and date is checkin
                        emp_attendance.check_out = date
                    else:
                        # date > checkin and > checkout, create new record  for it
                        vals = {
                            "employee_id": employee.id,
                            "check_in": date,
                        }
                        self.env["hr.attendance"].sudo().create(vals)
                        employee.attendance_state = "checked_in"
        else:
            # check if there is checkin & check
            # create a new attendance
            vals = {
                "employee_id": employee.id,
                "check_in": date,
            }
            self.env["hr.attendance"].sudo().create(vals)
            employee.attendance_state = "checked_in"

    def _get_biotime_token(self, biotime_url):
        biotime_username = (
            self.env["ir.config_parameter"].sudo().get_param("biotime_username", "")
        )
        biotime_password = (
            self.env["ir.config_parameter"].sudo().get_param("biotime_password", "")
        )
        data = {
            "username": biotime_username,
            "password": biotime_password,
        }
        headers = {"Content-Type": "application/json"}
        try:
            req = requests.post(
                biotime_url + "/api-token-auth/", json=data, headers=headers
            )
            token = json.loads(req.content).get("token")
            self.env["ir.config_parameter"].sudo().set_param("biotime_token", token)
        except Exception as e:
            _logger.info("Cannot get Biotime Token, Exception: %s", e)
        return token
