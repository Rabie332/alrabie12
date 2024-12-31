from odoo import api, fields, models


class ClearanceRequest(models.Model):
    _inherit = "clearance.request"

    @api.model
    def cron_clearance_request_reports(self):
        """Cron clearance request."""
        today = fields.Date.today()
        clearance_obj = self.env["clearance.request"]
        domain = [("state", "!=", "delivery_done")]
        domain_today = [("date_receipt", "=", today), ("state", "=", "delivery_done")]
        clearance_requests = clearance_obj.search(domain, order="id desc")
        clearance_requests_today = clearance_obj.search(domain_today, order="id desc")
        clearance_requests = clearance_requests + clearance_requests_today
        partner_ids = clearance_requests.mapped("partner_id")
        template = self.env.ref(
            "clearance_reports.mail_template_send_clearance_reports",
            raise_if_not_found=False,
        )
        if template:
            for partner in partner_ids:
                partner_id = self.env["res.partner"].search(
                    [("id", "=", partner.id)], limit=1
                )
                if partner_id.email:
                    template.email_to = partner_id.email
                    ctx = dict(
                        default_res_id=partner.id,
                        default_model="clearance.request",
                        default_template_id=template,
                    )
                    template.with_context(ctx).send_mail(partner.id, force_send=True)
