from odoo import api, models


class HrPeriod(models.Model):
    _inherit = "hr.period"

    @api.onchange("date_start", "date_end")
    def _onchange_date_start_end(self):
        """Calculate number_worked_days and number_worked_hours."""
        if self.date_start and self.date_end:
            self.number_worked_days = (self.date_end - self.date_start).days + 1
            self.number_worked_hours = (
                self.number_worked_days
                * self.env.user.company_id.resource_calendar_id.hours_per_day
            )
