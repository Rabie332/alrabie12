from odoo import models
from odoo.tools.misc import clean_context


class MailActivity(models.Model):
    _inherit = "mail.activity"

    def action_feedback(self, feedback=False, attachment_ids=None):
        self = self.with_context(clean_context(self.env.context))
        # Make activities as done that are related to Dms folders for all employees (users)
        if self.res_model == "dms.folder":
            messages, next_activities = self.sudo()._action_done(
                feedback=feedback, attachment_ids=attachment_ids
            )
        else:
            messages, next_activities = self._action_done(
                feedback=feedback, attachment_ids=attachment_ids
            )
        return messages.ids and messages.ids[0] or False
