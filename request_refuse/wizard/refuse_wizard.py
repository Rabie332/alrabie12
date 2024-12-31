from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class RefuseWizard(models.TransientModel):
    _name = "refuse.wizard"
    _description = "Refuse Wizard"

    message = fields.Text(string="Refusal reason")

    def button_refuse(self):
        """Action Refuse reason"""
        context = self.env.context or {}

        # Write Refuse message

        for record in self:
            if (
                record.message
                and context.get("active_id", False)
                and context.get("active_model", False)
            ):
                model_obj = self.env[context.get("active_model")]
                rec = model_obj.browse(context.get("active_id"))
                action_name = context.get("action_name", False)
                field_name = context.get("field_name", False)
                if field_name:
                    values = {field_name: record.message}
                    eval_dict = {"rec": rec, "values": values}
                    safe_eval("rec.write(values)", eval_dict)
                if action_name:
                    getattr(rec, action_name)()
