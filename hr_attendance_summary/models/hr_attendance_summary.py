import math
from datetime import datetime, time

import pytz

from odoo import api, fields, models


class HrAttendanceSummary(models.Model):
    _name = "hr.attendance.summary"
    _order = "date desc"
    _rec_name = "date"
    _description = "Hr attendance summary"

    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    line_ids = fields.One2many(
        "hr.attendance.summary.line", "summary_id", string="Summary lines"
    )

    _sql_constraints = [
        ("unique_date", "unique(date)", "The date of summary must be unique!"),
    ]


class HrAttendanceSummaryLine(models.Model):
    _name = "hr.attendance.summary.line"
    _order = "date desc"
    _rec_name = "date"
    _description = "Hr attendance summary line"

    check_in_date = fields.Datetime("Check In", compute="_compute_check_in_out_date")
    check_out_date = fields.Datetime("Check Out", compute="_compute_check_in_out_date")
    date = fields.Date(string="Date", related="summary_id.date", store=1)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    delay_hours_manuel = fields.Float(string="Manual Delay")
    delay_hours = fields.Float(
        string="Delay", compute="_compute_attendance_summary", store=True
    )
    worked_hours_manuel = fields.Float(string="Manual Hours worked")
    worked_hours = fields.Float(
        string="Hours worked", compute="_compute_attendance_summary", store=True
    )
    overtime_hours_manuel = fields.Float(string="Manual Overtime")
    overtime_hours = fields.Float(
        string="Overtime",
        compute="_compute_attendance_summary",
        store=True,
    )
    summary_id = fields.Many2one(
        "hr.attendance.summary", string="Summary", ondelete="cascade"
    )
    attendance_ids = fields.One2many(
        "hr.attendance", "summary_id", string="Attendance", readonly=True
    )
    presence_state = fields.Selection(
        string="Presence state",
        selection=[
            ("leave", "On leave"),
            ("absent", "Absent"),
            ("service", "In service"),
        ],
        default="service",
        required=True,
    )
    company_id = fields.Many2one(
        "res.company", related="employee_id.company_id", store=True
    )
    absence_hours = fields.Float(
        string="Absence Hours",
        compute="_compute_attendance_summary",
        store=True,
    )

    early_exit_hours = fields.Float(
        string="Early Exit Hours",
        compute="_compute_attendance_summary",
        store=True,
    )

    def float_time_convert(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        return factor * int(math.floor(val)), int(round((val % 1) * 60))

    def _format_date(self, naive_dt):
        naive = datetime.strptime(naive_dt, "%Y-%m-%d %H:%M:%S")
        tz_name = self.env.user.tz
        tz = pytz.timezone(tz_name) if tz_name else pytz.utc
        ran = pytz.utc.localize(naive).astimezone(tz)
        date = datetime.strptime(str(ran)[:19], "%Y-%m-%d %H:%M:%S")
        return date

    def check_exist_absence_justified(self, model, employee):
        """Check if employee has training or deputation or leave"""
        records = self.env[model].search(
            [
                ("employee_id", "=", employee.id),
                ("date_from", "<=", fields.Date.today()),
                ("date_to", ">=", fields.Date.today()),
                ("state", "=", "done"),
            ],
            limit=1,
        )
        return records

    def check_attendance_employee(self, employee, date_from, date_to):
        """Check if employee is in service (check in an check out)"""
        emp_attendance = (
            self.env["hr.attendance"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", employee.id),
                    ("check_in", ">=", date_from),
                    ("check_out", "<=", date_to),
                ],
                limit=1,
                order="check_in desc",
            )
        )
        return emp_attendance

    def get_summary(self, employee, date_from, date_to):
        """Get summary of employee"""
        summary_ids = self.env["hr.attendance.summary.line"].search(
            [
                ("employee_id", "=", employee.id),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
            ]
        )
        return summary_ids

    def create_summary_attendance(self):
        attendance_summary_object = self.env["hr.attendance.summary"]
        date_today = fields.Date.today()
        summary = attendance_summary_object.search([("date", "=", date_today)])
        if not summary:
            summary = attendance_summary_object.create({"date": date_today})
        for employee in self.env["hr.employee"].search(
            [("resource_calendar_id", "!=", False)]
        ):
            resource_calendar_attendances = self.env[
                "resource.calendar.attendance"
            ].search(
                [
                    ("calendar_id", "=", employee.resource_calendar_id.id),
                    ("dayofweek", "=", str(date_today.weekday())),
                ]
            )
            # Check if employee has summary on specific date
            count_summary = self.env["hr.attendance.summary.line"].search_count(
                [("employee_id", "=", employee.id), ("date", "=", date_today)]
            )
            leaves = self.env["hr.leave"].search(
                [
                    ("employee_id", "=", employee.id),
                    ("request_date_from", "<=", date_today),
                    ("request_date_to", ">=", date_today),
                    ("state", "=", "validate"),
                ]
            )
            values = {"employee_id": employee.id, "summary_id": summary.id}
            if resource_calendar_attendances and not count_summary:
                # Check if employee has leave:
                if leaves:
                    values.update({"presence_state": "leave"})
                else:
                    checkin_start = str(fields.Date.today()) + " 00:00:00"
                    checkin_end = str(fields.Date.today()) + " 23:59:59"
                    # Check attendance of employee if he don't check in he is absent
                    emp_attendance = self.check_attendance_employee(
                        employee, checkin_start, checkin_end
                    )
                    presence_state = "service" if emp_attendance else "absent"
                    values.update({"presence_state": presence_state})
                summary_line = self.env["hr.attendance.summary.line"].create(values)
                summary_line._compute_attendance_summary()

    def update_summary_attendance(self, record):
        """Update summary attendance"""
        # check if the record has fields date_from and date_to
        if (
            record.state == "cancel"
            and "date_from" in record._fields
            and "date_to" in record._fields
        ):
            checkin_start = str(fields.Date.today()) + " 00:00:00"
            checkin_end = str(fields.Date.today()) + " 23:59:59"
            # Check attendance of employee if he don't check in he is absent
            emp_attendance = self.check_attendance_employee(
                record.employee_id, checkin_start, checkin_end
            )
            presence_state = "service" if emp_attendance else "absent"
            summary_ids = self.get_summary(
                record.employee_id, record.date_from, record.date_to
            )
            if summary_ids:
                summary_ids.write({"presence_state": presence_state})

    @api.depends(
        "attendance_ids.check_in",
        "attendance_ids.check_out",
        "overtime_hours_manuel",
        "worked_hours_manuel",
        "delay_hours_manuel",
        "early_exit_hours",
    )
    def _compute_attendance_summary(self):
        for record in self:
            record.worked_hours = record.worked_hours_manuel
            record.delay_hours = record.delay_hours_manuel
            record.overtime_hours = record.overtime_hours_manuel
            record.early_exit_hours = record.overtime_hours_manuel
            hours_per_day = record.employee_id.resource_calendar_id.hours_per_day
            if record.attendance_ids:
                # calculate overtime
                record.worked_hours = sum(record.attendance_ids.mapped("worked_hours"))
                calendar_attendances = (
                    record.employee_id.resource_calendar_id.attendance_ids.filtered(
                        lambda x: x.dayofweek == str(record.date.weekday())
                    )
                )
                calendar_worked_hours = 0
                for attendance in calendar_attendances:
                    calendar_worked_hours += attendance.hour_to - attendance.hour_from
                overtime_hours = record.worked_hours - calendar_worked_hours
                # caculate absence_hours
                worked_hours = (
                    record.worked_hours
                    if record.worked_hours <= hours_per_day
                    else hours_per_day
                )
                record.absence_hours = hours_per_day - worked_hours
                record.overtime_hours += overtime_hours if overtime_hours > 0 else 0
                # calculate delay if employee has calendar attendance for
                # the current day
                first_sign_in_hour = 0
                last_sign_out_hour = 0
                attendance_last_sign_out_hour = 0
                if calendar_attendances:
                    first_sign_in_hour = (
                        calendar_attendances.sorted("hour_from")[0].hour_from
                        + record.employee_id.resource_calendar_id.late
                    )
                    # get last sign out in calender with early exit hours
                    last_sign_out_hour = (
                        calendar_attendances.sorted("hour_to")[0].hour_to
                        - record.employee_id.resource_calendar_id.early_exit
                    )
                attendance_first_sign_in_hour = record.attendance_ids.sorted(
                    key=lambda r: r.check_in
                )[0].check_in

                attendance_first_sign_in_hour = self._format_date(
                    str(attendance_first_sign_in_hour)
                )

                attendance_first_sign_in_hour = (
                    attendance_first_sign_in_hour.time().replace(second=0)
                )
                hour_start, min_start = self.float_time_convert(first_sign_in_hour)
                first_sign_in_hour = time(int(hour_start), int(min_start), 0)
                if record.attendance_ids.filtered(lambda p: p.check_out):
                    # get last sign out of employee
                    attendance_last_sign_out_hour = (
                        record.attendance_ids.filtered(lambda p: p.check_out)
                        .sorted(key=lambda r: r.check_out)[0]
                        .check_out
                    )
                    if attendance_last_sign_out_hour:

                        attendance_last_sign_out_hour = self._format_date(
                            str(attendance_last_sign_out_hour)
                        )

                        attendance_last_sign_out_hour = (
                            attendance_last_sign_out_hour.time().replace(second=0)
                        )
                        (
                            hour_start_last_sign_out_hour,
                            min_start_last_sign_out_hour,
                        ) = self.float_time_convert(last_sign_out_hour)
                        last_sign_out_hour = time(
                            int(hour_start_last_sign_out_hour),
                            int(min_start_last_sign_out_hour),
                            0,
                        )
                # calculate late houres
                if attendance_first_sign_in_hour > first_sign_in_hour:
                    delay = datetime.strptime(
                        str(attendance_first_sign_in_hour), "%H:%M:%S"
                    ) - datetime.strptime(str(first_sign_in_hour), "%H:%M:%S")
                    delay_seconds = delay.seconds
                    delay = delay_seconds / 3600.0
                    record.delay_hours += delay
                # calculate early exit hours
                if last_sign_out_hour and attendance_last_sign_out_hour:
                    if attendance_last_sign_out_hour < last_sign_out_hour:
                        early_exit = datetime.strptime(
                            str(last_sign_out_hour), "%H:%M:%S"
                        ) - datetime.strptime(
                            str(attendance_last_sign_out_hour), "%H:%M:%S"
                        )
                        early_exit_hours = early_exit.seconds / 3600.0
                        record.early_exit_hours = early_exit_hours

    @api.depends("attendance_ids")
    def _compute_check_in_out_date(self):
        """Get the first check in and last check out time in each day"""
        for summary in self:
            summary.check_in_date = summary.check_out_date = False
            if summary.attendance_ids:
                summary.check_in_date = summary.attendance_ids.sorted("check_in")[
                    0
                ].check_in
                summary.check_out_date = summary.attendance_ids.search(
                    [("summary_id", "=", summary.id), ("check_out", "!=", False)],
                    order="check_out desc",
                    limit=1,
                ).check_out
