from odoo import fields, models


class AccountEntryReportWizard(models.TransientModel):
    _name = "account.entry.report.wizard"
    _description = "Account Entries Report"

    date_from = fields.Date(string="Start Date", required=1)
    date_to = fields.Date(string="End Date", required=1)
    is_posted_entry = fields.Boolean(string="Posted Entry")

    def name_get(self):
        """Get Complete name.

        :return: List of tuples of  (date_to, date_from)
        """
        result = []
        for record in self:
            name = "{} - {} ".format(record.date_from, record.date_to)
            result.append((record.id, name))
        return result

    def print_report(self):
        """Print entries report pdf."""
        data = {"ids": [self.id], "form": self.read([])[0]}
        return self.env.ref("account_move_report.account_entry_report").report_action(
            self, data=data
        )

    def print_xls_report(self):
        """Print entries report XlSX."""
        data = {"ids": [self.id], "form": self.read([])[0]}
        return self.env.ref(
            "account_move_report.account_entry_template_xlsx"
        ).report_action(self, data=data)
