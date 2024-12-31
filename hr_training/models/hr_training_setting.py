from odoo import _, api, fields, models


class HrTrainingSetting(models.Model):
    _name = "hr.training.setting"
    _description = "Training Setting"

    name = fields.Char(string="Name", default="Training Setting", translate=True)
    annual_balance = fields.Integer(string="Annual Balance")
    line_ids = fields.One2many(
        "hr.training.allowance", "training_setting_id", string="Details"
    )
    balance_training_no_specified = fields.Boolean("Balance Training Not Specified")
    accumulative_balance = fields.Boolean(string="Accumulative Balance")

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------
    def button_setting(self):
        """Show view form for training main settings.

        :return: Dictionary contain view form of hr.training.setting
        """
        training_setting = self.env["hr.training.setting"].search([], limit=1)
        if training_setting:
            value = {
                "name": _("Training Setting"),
                "view_type": "form",
                "view_mode": "form",
                "res_model": "hr.training.setting",
                "view_id": False,
                "type": "ir.actions.act_window",
                "res_id": training_setting.id,
            }
            return value


class HrTrainingAllowance(models.Model):
    _name = "hr.training.allowance"
    _description = "Allowance"

    name = fields.Char(string="Name")
    training_setting_id = fields.Many2one(
        "hr.training.setting", string="Setting", ondelete="cascade"
    )
    internal_training_amount = fields.Float(string="Internal Training Amount")
    external_training_amount = fields.Float(string="External Training Amount")
    internal_transport_amount = fields.Float(string="Internal Transport Amount")
    external_transport_amount = fields.Float(string="External Transport Amount")
    travel_days_ids = fields.One2many(
        "training.travel.days", "training_allowance_id", string="Travel Days"
    )
    food = fields.Integer("Food %")
    transport = fields.Integer("Transport %")
    hosing = fields.Integer("Hosing %")

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------
    def _get_allowance_domain(self, training):
        return []

    def get_allowance(self, training):
        domain = self._get_allowance_domain(training)
        return self.search(domain, limit=1)

    @api.model
    def get_training_allowance_amount(self, location_type, training):
        """Calculate allowance amounts depend on the main training configuration.

        :param number_of_days: Integer
        :param location_type: selection
        :param Employee: Many2one
        :return: Triple floats (training_amount: Float)
        """
        training_amount = transport_amount = 0.0
        # To do get training allowance by position
        training_allowance = self.get_allowance(training)
        if training_allowance:
            if location_type == "internal":
                training_amount = training_allowance.internal_training_amount
                transport_amount = training_allowance.internal_transport_amount
            else:
                training_amount = training_allowance.external_training_amount
                transport_amount = training_allowance.external_transport_amount
        return training_amount, transport_amount

    @api.model
    def get_travel_days(self, country_id, training):
        """Calculate travel days  depend on the main training configuration.

        :param training: Many2one
        :param country_id: Many2one
        :return: travel_days: Selection
        """
        # to do get training balance with job position
        training_allowance = self.get_allowance(training)
        if training_allowance:
            group_country_id = self.env["res.country.group"].search(
                [("country_ids", "in", [country_id.id])], limit=1
            )
            if group_country_id:
                travel_days = (
                    self.env["training.travel.days"]
                    .search(
                        [
                            ("training_allowance_id", "=", training_allowance.id),
                            ("country_group_id", "=", group_country_id.id),
                        ]
                    )
                    .travel_days
                )
                if travel_days:
                    return travel_days


class TrainingTravelDays(models.Model):
    _name = "training.travel.days"
    _description = "Travel Days"

    country_group_id = fields.Many2one(
        "res.country.group", required=1, string="Country categories"
    )
    travel_days = fields.Selection(
        [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")],
        required=1,
        string="Travel Days",
    )
    training_allowance_id = fields.Many2one(
        "hr.training.allowance", string="Allowance", ondelete="cascade"
    )
