from odoo import _, api, fields, models


class HrDeputationSetting(models.Model):
    _name = "hr.deputation.setting"
    _description = "Deputation Setting"

    name = fields.Char(string="name", default="Deputation Setting")
    annual_balance = fields.Integer(string="Annual Balance")
    line_ids = fields.One2many(
        "hr.deputation.allowance", "deputation_setting_id", string="Details"
    )
    deputation_with_kilometer = fields.Boolean(string="With kilometer")
    deputation_with_travel_dates = fields.Boolean("Travel Dates")
    count_public_holidays = fields.Boolean("Public holidays included")
    balance_deputation_no_specified = fields.Boolean("Balance Deputation Not Specified")
    multiply_deputation_days = fields.Boolean(string="Doubling the days of deputation")
    multiply_deputation_holidays_days = fields.Float(
        string="Doubling the holidays days By", default=1
    )
    accumulative_balance = fields.Boolean(string="Accumulative Balance")

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------
    def button_setting(self):
        """Show view form for deputation main settings.

        :return: Dictionary contain view form of hr.deputation.setting
        """
        deputation_setting = self.env["hr.deputation.setting"].search([], limit=1)
        if deputation_setting:
            value = {
                "name": _("Deputation Setting"),
                "view_type": "form",
                "view_mode": "form",
                "res_model": "hr.deputation.setting",
                "view_id": False,
                "type": "ir.actions.act_window",
                "res_id": deputation_setting.id,
            }
            return value

    # ------------------------------------------------------------
    # Onchange methods
    # ------------------------------------------------------------
    @api.onchange("multiply_deputation_days")
    def _onchange_multiply_deputation_days(self):
        if not self.multiply_deputation_days:
            self.multiply_deputation_holidays_days = 0


class HrDeputationAllowance(models.Model):
    _name = "hr.deputation.allowance"
    _description = "Allowance"

    name = fields.Char(string="name", translate=True)
    deputation_setting_id = fields.Many2one(
        "hr.deputation.setting", string="Setting", ondelete="cascade"
    )
    internal_deputation_amount = fields.Float(string="Internal Deputation Amount")
    external_deputation_amount = fields.Float(string="External Deputation Amount")
    internal_transport_amount = fields.Float(string="Internal Transport Amount")
    external_transport_amount = fields.Float(string="External Transport Amount")
    travel_days_ids = fields.One2many(
        "travel.days", "deputation_allowance_id", string="Travel Days"
    )
    food = fields.Integer("Food %")
    transport = fields.Integer("Transport %")
    hosing = fields.Integer("Hosing %")
    deputation_kilometer_ids = fields.One2many(
        "hr.deputation.kilometer", "deputation_allowance_id", string="kilometer Amounts"
    )
    ticket_type = fields.Selection(
        [("economic", "Economic"), ("business", "Business")],
        default="economic",
        string="Ticket Type",
    )
    is_amount_kilometers = fields.Boolean(string="Is amount kilometer")
    kilometer_limit = fields.Float(string="Kilometer limit Overland")
    kilometer_amount = fields.Float(string="Kilometer Amount Overland")

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------
    def _get_allowance_domain(self, deputation):
        return []

    def get_allowance(self, deputation):
        domain = self._get_allowance_domain(deputation)
        return self.search(domain, limit=1)

    def get_allowance_kilometer(self, deputation):
        domain = self._get_allowance_domain(deputation)
        domain.append(("is_amount_kilometers", "=", True))
        domain.append(("deputation_setting_id.deputation_with_kilometer", "=", False))
        return self.search(domain, limit=1)

    def _get_ticket_type(self, deputation):
        deputation_allowance = self.get_allowance(deputation)
        return deputation_allowance.ticket_type

    def get_deputation_allowance_amount(self, location_type, deputation):
        """Calculate allowance amounts depend on the main deputation configuration.

        :param number_of_days: Integer
        :param location_type: selection
        :param Employee: Many2one
        :return: Triple floats (deputation_amount: Float)
        """
        deputation_amount = transport_amount = 0.0
        # To do get deputation allowance by position
        deputation_allowance = self.get_allowance(deputation)
        if deputation_allowance:
            if location_type == "internal":
                deputation_amount = deputation_allowance.internal_deputation_amount
                transport_amount = deputation_allowance.internal_transport_amount
            else:
                deputation_amount = deputation_allowance.external_deputation_amount
                transport_amount = deputation_allowance.external_transport_amount
        return deputation_amount, transport_amount

    def get_deputation_allowance_kilometer_amount(self, deputation):
        deputation_allowance = self.get_allowance_kilometer(deputation)
        kilometer_amount = (
            deputation_allowance.kilometer_amount
            if deputation_allowance.kilometer_limit
            and deputation.distance
            and deputation_allowance.kilometer_limit >= deputation.distance
            else 0
        )
        return kilometer_amount, deputation_allowance

    def get_travel_days(self, country_id, deputation):
        """Calculate travel days  depend on the main deputation configuration.

        :param deputation: Many2one
        :param country_id: Many2one
        :return: travel_days: Selection
        """
        # to do get deputation balance with job position
        deputation_allowance = self.get_allowance(deputation)
        if deputation_allowance:
            group_country_id = self.env["res.country.group"].search(
                [("country_ids", "in", [country_id.id])], limit=1
            )
            if group_country_id:
                travel_days = (
                    self.env["travel.days"]
                    .search(
                        [
                            ("deputation_allowance_id", "=", deputation_allowance.id),
                            ("country_group_id", "=", group_country_id.id),
                        ]
                    )
                    .travel_days
                )
                if travel_days:
                    return travel_days

    def get_kilometer_amount(self, deputation):
        """Calculate travel days  depend on the main deputation configuration.

        :param deputation: Many2one
        :return: kilometer_amount: Float
        """
        # to do get deputation balance with job position
        deputation_allowance = self.get_allowance(deputation)
        kilometer_amount = 0
        if deputation_allowance:
            deputation_kilometer = self.env["hr.deputation.kilometer"].search(
                [
                    ("deputation_allowance_id", "=", deputation_allowance.id),
                    ("kilometer_from", "<=", deputation.distance),
                    ("kilometer_to", ">=", deputation.distance),
                ],
                limit=1,
            )
            if deputation_kilometer:
                kilometer_amount = deputation_kilometer.kilometer_amount
        return kilometer_amount

    @api.onchange("is_amount_kilometers")
    def _onchange_amount_kilometers(self):
        self.kilometer_limit = self.kilometer_amount = 0


class TravelDays(models.Model):
    _name = "travel.days"
    _description = "Travel Days"

    country_group_id = fields.Many2one(
        "res.country.group", required=1, string="Country categories"
    )
    travel_days = fields.Selection(
        [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")],
        required=1,
        string="Travel Days",
    )
    deputation_allowance_id = fields.Many2one(
        "hr.deputation.allowance", string="Allowance", ondelete="cascade"
    )


class HrDeputationkilometer(models.Model):
    _name = "hr.deputation.kilometer"
    _description = "Hr Deputation kilometer"

    kilometer_from = fields.Integer("kilometer From")
    kilometer_to = fields.Integer("kilometer To")
    kilometer_amount = fields.Float("kilometer Amount")
    deputation_allowance_id = fields.Many2one(
        "hr.deputation.allowance", string="Allowance", ondelete="cascade"
    )
