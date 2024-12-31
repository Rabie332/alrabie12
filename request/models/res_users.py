from odoo import api, fields, models, modules


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def systray_get_activities(self):
        """Surchage method to not counting unactive activity by adding active='t' to query."""
        query = """SELECT m.id, count(*), act.res_model as model,
                           CASE
                               WHEN %(today)s::date - act.date_deadline::date = 0 Then 'today'
                               WHEN %(today)s::date - act.date_deadline::date > 0 Then 'overdue'
                               WHEN %(today)s::date - act.date_deadline::date < 0 Then 'planned'
                           END AS states
                       FROM mail_activity AS act
                       JOIN ir_model AS m ON act.res_model_id = m.id
                       WHERE user_id = %(user_id)s and active='t'
                       GROUP BY m.id, states, act.res_model;
                       """
        self.env.cr.execute(
            query, {"today": fields.Date.context_today(self), "user_id": self.env.uid}
        )
        activity_data = self.env.cr.dictfetchall()
        model_ids = [a["id"] for a in activity_data]
        model_names = {
            n[0]: n[1] for n in self.env["ir.model"].browse(model_ids).name_get()
        }

        user_activities = {}
        for activity in activity_data:
            if not user_activities.get(activity["model"]):
                module = self.env[activity["model"]]._original_module
                icon = module and modules.module.get_module_icon(module)
                user_activities[activity["model"]] = {
                    "name": model_names[activity["id"]],
                    "model": activity["model"],
                    "type": "activity",
                    "icon": icon,
                    "total_count": 0,
                    "today_count": 0,
                    "overdue_count": 0,
                    "planned_count": 0,
                }
            user_activities[activity["model"]][
                "%s_count" % activity["states"]
            ] += activity["count"]
            if activity["states"] in ("today", "overdue"):
                user_activities[activity["model"]]["total_count"] += activity["count"]

            user_activities[activity["model"]]["actions"] = [
                {"icon": "fa-clock-o", "name": "Summary"}
            ]
        return list(user_activities.values())
