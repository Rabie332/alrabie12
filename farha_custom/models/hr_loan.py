from odoo import models


class HrLoan(models.Model):
    _inherit = "hr.loan"

    # ------------------------------------------------------------
    # Constraints methods
    # ------------------------------------------------------------
    def _check_employee(self):
        """Inherit _check_employee: to remove all checks."""
        return True
