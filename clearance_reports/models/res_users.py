from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    def get_clreances(self, request_types):
        """Get clearance changed to state transport today."""
        # get tracking lines for today
        # pylint: disable=sql-injection
        self.env.cr.execute(
            """SELECT res_id FROM mail_message WHERE model='%s' and date::date = '%s'"""
            % ("clearance.request", fields.Date.today())
        )
        clearance_ids = list({clearance[0] for clearance in self.env.cr.fetchall()})
        tracking_lines = (
            self.env["mail.tracking.value"]
            .sudo()
            .search(
                [
                    ("mail_message_id.res_id", "in", clearance_ids),
                    ("new_value_char", "in", ["Transport", "نقل"]),
                ]
            )
        )
        # get clearances from tracking lines
        clearance_ids = tracking_lines.mapped("mail_message_id.res_id")
        clearance_data = self.env["clearance.request"].search(
            [
                ("id", "in", clearance_ids),
                ("request_type", "in", request_types),
                ("company_id", "=", self.company_id.id),
            ]
        )
        return clearance_data

    def _get_clearances_transport(self, request_types):
        return self.get_clreances(request_types)

    def _cron_send_email_clearances_transport(self):
        """This cron will :
        - send email to user with report of today transaction transport
        """
        template = self.env.ref(
            "clearance_reports.user_template_today_transaction",
            raise_if_not_found=False,
        )
        users_transportation = self.env["res.users"].search(
            [
                (
                    "groups_id",
                    "in",
                    self.env.ref("transportation.group_transportation_responsible").id,
                ),
                ("email", "!=", False),
            ]
        )
        for user in users_transportation:
            clearances = user.get_clreances(["clearance", "transport", "other_service"])
            if template and user.id and clearances:
                template.send_mail(user.id, force_send=True)
