from odoo import http

from odoo.addons.mail.controllers.main import MailController


class HrAuthorizationController(http.Controller):
    @http.route("/authorization/approve", type="http", auth="user", methods=["GET"])
    def hr_authorization_request_validate(self, res_id, token):
        (
            comparison,
            record,
            redirect,
        ) = MailController._check_token_and_record_or_redirect(
            "hr.authorization", int(res_id), token
        )
        if comparison and record:
            try:
                record.action_second_approve()
            except Exception:
                return MailController._redirect_to_messaging()
        return redirect

    @http.route("/authorization/refuse", type="http", auth="user", methods=["GET"])
    def hr_authorization_request_refuse(self, res_id, token):
        (
            comparison,
            record,
            redirect,
        ) = MailController._check_token_and_record_or_redirect(
            "hr.authorization", int(res_id), token
        )
        if comparison and record:
            try:
                record.action_refuse()
            except Exception:
                return MailController._redirect_to_messaging()
        return redirect
