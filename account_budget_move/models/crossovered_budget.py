from odoo import models


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    def name_get(self):
        result = []
        for record in self:
            name = "{} [{}]".format(
                record.general_budget_id.name, record.planned_amount
            )
            result.append((record.id, name))
        return result
