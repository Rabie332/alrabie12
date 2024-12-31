from odoo import _, fields, models


class HrFinancialCovenantSetting(models.Model):
    _name = "hr.financial.covenant.setting"
    _description = "Financial Covenant Setting"

    name = fields.Char("Name", default="Financial Covenant Setting", translate=1)
    financial_covenant_move_ids = fields.One2many(
        "hr.financial.covenant.move",
        "financial_covenant_setting_id",
        string="Financial Covenant Moves",
    )

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------
    def button_setting(self):
        """Show view form for financial covenant main settings.

        :return: Dictionary contain view form of hr.financial.covenant.setting
        """
        financial_covenant_setting = self.env["hr.financial.covenant.setting"].search(
            [], limit=1
        )
        if financial_covenant_setting:
            value = {
                "name": _("Financial Covenant Setting"),
                "view_type": "form",
                "view_mode": "form",
                "res_model": "hr.financial.covenant.setting",
                "view_id": False,
                "type": "ir.actions.act_window",
                "res_id": financial_covenant_setting.id,
            }
            return value


class HrFinancialCovenantMove(models.Model):
    _name = "hr.financial.covenant.move"
    _description = "Financial Covenant Move"

    account_id = fields.Many2one(
        "account.account",
        required=1,
        string="Account",
        domain="[('user_type_id.type', 'in', ('receivable', 'payable'))"
        ", ('company_id', '=', company_id)]",
    )
    journal_id = fields.Many2one(
        "account.journal",
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]",
        required=1,
        string="Journal",
    )
    company_id = fields.Many2one("res.company", string="Company")
    financial_covenant_setting_id = fields.Many2one(
        "hr.financial.covenant.setting", string="Setting"
    )
