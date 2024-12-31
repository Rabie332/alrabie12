from datetime import date, datetime, time
import babel
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

# get_worked_day_lines
class HrPayslip(models.Model):
    _inherit = "hr.payslip"
    
    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = []
        for contract in contracts.filtered(lambda c: c.resource_calendar_id):
            day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
            day_to = datetime.combine(fields.Date.from_string(date_to), time.max)

            leaves = {}
            calendar = contract.resource_calendar_id
            tz = timezone(calendar.tz)

            # Assuming contract.employee_id.list_leaves() is a method that returns leave intervals
            day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to, calendar=calendar)
            for day, hours, leave in day_leave_intervals:
                holiday = leave.holiday_id

                # Process each leave type individually by iterating through the holiday recordset
                for holiday_status_id in holiday.mapped('holiday_status_id'):
                    leave_type_key = holiday_status_id.id

                    if leave_type_key not in leaves:
                        leaves[leave_type_key] = {
                            "name": holiday_status_id.name or _("Global Leaves"),
                            "sequence": 5,
                            "code": holiday_status_id.name or "GLOBAL",
                            "number_of_days": 0.0,
                            "number_of_hours": 0.0,
                            "contract_id": contract.id,
                        }

                    leaves[leave_type_key]["number_of_hours"] += hours
                    work_hours = calendar.get_work_hours_count(
                        tz.localize(datetime.combine(day, time.min)),
                        tz.localize(datetime.combine(day, time.max)),
                        compute_leaves=False,
                    )
                    if work_hours:
                        leaves[leave_type_key]["number_of_days"] += hours / work_hours

            work_data = contract.employee_id._get_work_days_data(day_from, day_to, calendar=calendar)
            attendances = {
                "name": _("Normal Working Days paid at 100%"),
                "sequence": 1,
                "code": "WORK100",
                "number_of_days": work_data["days"],
                "number_of_hours": work_data["hours"],
                "contract_id": contract.id,
            }

            res.append(attendances)
            res.extend(leaves.values())
        return res
    