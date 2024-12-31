from odoo.api import Environment


def migrate(cr, version):
    """Create bonus line for previous bonus."""
    env = Environment(cr, 1, context={})
    bonus_ids = env["hr.bonus"].sudo().search([("line_ids", "=", False)])
    for bonus in bonus_ids:
        if bonus.bonus_method == "amount" and bonus.amount:
            for employee in bonus.employee_ids:
                env["hr.bonus.line"].create(
                    {
                        "employee_id": employee.id,
                        "base_amount": 0,
                        "percent": 0,
                        "net_amount": bonus.amount,
                        "amount": bonus.amount,
                        "bonus_id": bonus.id,
                    }
                )
