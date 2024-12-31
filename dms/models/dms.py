import ast
import json
from datetime import date, datetime

from babel.dates import format_date
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.osv import expression
from odoo.release import version
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class DmsTag(models.Model):
    _name = "dms.tag"
    _description = "Tags"

    name = fields.Char(string="Name", required=1)
    color = fields.Integer(string="Color Index")


class DmsCabinet(models.Model):
    _name = "dms.cabinet"
    _description = "Cabinets"

    name = fields.Char(string="Name", required=1)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )
    drawer_ids = fields.One2many("dms.drawer", "cabinet_id", string="Drawers")


class DmsDrawer(models.Model):
    _name = "dms.drawer"
    _description = "Drawers"

    name = fields.Char(string="Name", required=1)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )
    cabinet_id = fields.Many2one(
        "dms.cabinet", string="Cabinets", ondelete="cascade", index=True
    )


class DmsSettings(models.Model):
    _name = "dms.settings"
    _description = "General settings"

    name = fields.Char(string="Name")

    def open_settings(self):
        """Show view form for dms main settings.

        :return: Dictionary contain view form of dms.settings
        """
        settings = self.env["dms.settings"].search([], limit=1)
        if settings:
            value = {
                "name": "General settings",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "dms.settings",
                "view_id": False,
                "type": "ir.actions.act_window",
                "res_id": settings.id,
            }
            return value


class DmsSecrecy(models.Model):
    _name = "dms.secrecy"
    _description = "Secrecy"

    code = fields.Char(string="Code")
    name = fields.Char(string="Name", required=1)
    group_ids = fields.Many2many("res.groups", string="Groups")


class DmsFolder(models.Model):
    _name = "dms.folder"
    _inherit = ["mail.alias.mixin", "mail.thread", "mail.activity.mixin"]
    _description = "Folders"

    name = fields.Char(string="Name", required=1, index=True)
    active = fields.Boolean(default=True)
    code = fields.Char(string="Code", readonly=1)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )
    parent_folder_id = fields.Many2one("dms.folder", string="Main folder", index=True)
    cabinet_id = fields.Many2one("dms.cabinet", string="Cabinet")
    image = fields.Binary(string="Image", attachment=True)
    group_ids = fields.Many2many("res.groups", string="Groups")
    tag_ids = fields.Many2many("dms.tag", string="Tags")
    child_ids = fields.One2many("dms.folder", "parent_folder_id", string="Sub Folders")
    documents_ids = fields.One2many("ir.attachment", "folder_id", string="Documents")
    folders_count = fields.Integer(
        compute="_compute_folders_count", string="Number of Sub Folders"
    )
    documents_count = fields.Integer(
        compute="_compute_documents_count", string="Number of Documents"
    )
    color = fields.Integer(string="Color")
    favorite_user_ids = fields.Many2many(
        "res.users", "favorite_folder_users_rel", string="Users"
    )
    is_favorite = fields.Boolean(string="My favorite", compute="_compute_is_favorite")
    alias_id = fields.Many2one(
        "mail.alias", string="Email Aliases", ondelete="restrict"
    )
    dashboard_graph_data = fields.Text(compute="_compute_dashboard_graph")
    dashboard_graph_type = fields.Selection(
        [("line", "Line"), ("bar", "Bar")],
        string="Type",
        compute="_compute_dashboard_graph",
    )
    dashboard_graph_model = fields.Selection(
        [("ir.attachment", "Documents")], default="ir.attachment", string="Content"
    )
    dashboard_graph_group = fields.Selection(
        [("day", "Day"), ("week", "Week"), ("month", "Month")],
        string="Group by",
        default="day",
    )
    dashboard_graph_period = fields.Selection(
        [("week", "Last week"), ("month", "Last month"), ("year", "Last year")],
        string="Period",
        default="month",
    )
    locked = fields.Boolean(string="Locked")
    shared_user_ids = fields.Many2many("res.users", string="Employees")

    @api.model
    def create(self, vals):
        """Add sequence."""
        number_folder = self.env["ir.sequence"].next_by_code("dms.folder.seq")
        vals.update({"code": number_folder})
        return super(DmsFolder, self).create(vals)

    def write(self, vals):
        if vals.get("active") or vals.get("active") is False:
            # `vals.get('active') is False` means it's 'Unarchiving' action.
            if not self.env.user.has_group("dms.dms_group_archive_folders"):
                raise AccessError(
                    _("You don't have the access right to archive folders")
                )
        return super(DmsFolder, self).write(vals)

    @api.depends("child_ids.parent_folder_id")
    def _compute_folders_count(self):
        """Count the number of subfolders."""
        for record in self:
            record.folders_count = self.env["dms.folder"].search_count(
                [("parent_folder_id", "=", record.id)]
            )

    @api.depends("documents_ids.folder_id", "documents_ids.secrecy_id")
    def _compute_documents_count(self):
        """Count the number of documents inside the folder."""
        for record in self:
            record.documents_count = self.env["ir.attachment"].search_count(
                [("folder_id", "=", record.id)]
            )

    def add_remove_favorite(self):
        """Add and remove folder to favorite ."""
        if self.env.user not in self.favorite_user_ids:
            self.favorite_user_ids = [(4, self.env.uid)]
        else:
            self.favorite_user_ids = [(3, self.env.uid)]

    def _compute_is_favorite(self):
        """Check if the folder is favorite for current user."""
        for rec in self:
            if rec.env.user in rec.favorite_user_ids:
                rec.is_favorite = True
            else:
                rec.is_favorite = False

    def _alias_get_creation_values(self):
        values = super(DmsFolder, self)._alias_get_creation_values()
        values["alias_model_id"] = self.env["ir.model"]._get("dms.folder").id
        if self.id:
            values["alias_defaults"] = defaults = ast.literal_eval(
                self.alias_defaults or "{}"
            )
            defaults["category_id"] = self.id
        return values

    def get_alias_values(self):
        """Get alias values."""
        values = super(DmsFolder, self).get_alias_values()
        values["alias_defaults"] = {"folder_id": self.id}
        return values

    def _get_dashboard_graph_data(self):
        def get_week_name(start_date, locale):
            """Generates a week name (string) from a datetime according to the locale:
            E.g.: locale    start_date (datetime)      return string
                  "en_US"      November 16th           "16-22 Nov"
                  "en_US"      December 28th           "28 Dec-3 Jan"
            """
            if (start_date + relativedelta(days=6)).month == start_date.month:
                short_name_from = format_date(start_date, "d", locale=locale)
            else:
                short_name_from = format_date(start_date, "d MMM", locale=locale)
            short_name_to = format_date(
                start_date + relativedelta(days=6), "d MMM", locale=locale
            )
            return short_name_from + "-" + short_name_to

        self.ensure_one()
        values = []
        today = fields.Date.from_string(fields.Date.context_today(self))
        start_date, end_date = self._graph_get_dates(today)
        graph_data = self._graph_data(start_date, end_date)
        x_field = "label"
        y_field = "value"

        # generate all required x_fields and update the y_values where we have data for them
        locale = self._context.get("lang") or "en_US"

        weeks_in_start_year = int(
            date(start_date.year, 12, 28).isocalendar()[1]
        )  # This date is always in the last week of ISO years
        for week in range(
            0,
            (end_date.isocalendar()[1] - start_date.isocalendar()[1])
            % weeks_in_start_year
            + 1,
        ):
            short_name = get_week_name(
                start_date + relativedelta(days=7 * week), locale
            )
            values.append({x_field: short_name, y_field: 0})

        for data_item in graph_data:
            x_value = data_item.get("x_value")
            if isinstance(x_value, datetime):
                x_value = x_value.isocalendar()[1]
            if isinstance(x_value, date):
                x_value = x_value.isocalendar()[1]
            index = int((x_value - start_date.isocalendar()[1]) % weeks_in_start_year)
            values[index][y_field] = data_item.get("y_value")

        [graph_title, graph_key] = self._graph_title_and_key()
        color = "#875A7B" if "+e" in version else "#7c7bad"
        return [
            {
                "values": values,
                "area": True,
                "title": graph_title,
                "key": graph_key,
                "color": color,
            }
        ]

    @api.depends(
        "dashboard_graph_group", "dashboard_graph_model", "dashboard_graph_period"
    )
    def _compute_dashboard_graph(self):
        """Get  graph values."""
        for rec in self:
            if (
                rec.dashboard_graph_period == "week"
                and rec.dashboard_graph_group != "day"
                or rec.dashboard_graph_period == "month"
                and rec.dashboard_graph_group != "day"
            ):
                rec.dashboard_graph_type = "bar"
            else:
                rec.dashboard_graph_type = "line"
            rec.dashboard_graph_data = json.dumps(rec._get_dashboard_graph_data())

    def _graph_get_dates(self, today):
        """Return a coherent start and end date for the dashboard graph
        according to the graph settings."""
        if self.dashboard_graph_period == "week":
            start_date = today - relativedelta(weeks=1)
        elif self.dashboard_graph_period == "year":
            start_date = today - relativedelta(years=1)
        else:
            start_date = today - relativedelta(months=1)

        # we take the start of the following month/week/day if we group by
        # month/week/day
        # (to avoid having twice the same month/week/day
        # from different years/month/week)
        if self.dashboard_graph_group == "month":
            start_date = date(
                start_date.year + start_date.month // 12, start_date.month % 12 + 1, 1
            )
            # handle period=week, grouping=month for silly managers
            if self.dashboard_graph_period == "week":
                start_date = today.replace(day=1)
        elif self.dashboard_graph_group == "week":
            start_date += relativedelta(days=8 - start_date.isocalendar()[2])
            # add a week to make sure no overlapping is possible in case of year period
            # (will display max 52 weeks, avoid case of 53 weeks in a year)
            if self.dashboard_graph_period == "year":
                start_date += relativedelta(weeks=1)
        else:
            start_date += relativedelta(days=1)

        return [start_date, today]

    def _graph_date_column(self):
        """Get graph date column."""
        return "create_date"

    def _graph_x_query(self):
        """Get graph x query."""
        if self.dashboard_graph_group == "week":
            return "EXTRACT(WEEK FROM %s)" % self._graph_date_column()
        elif self.dashboard_graph_group == "month":
            return "EXTRACT(MONTH FROM %s)" % self._graph_date_column()
        else:
            return "DATE(%s)" % self._graph_date_column()

    def _graph_y_query(self):
        """Get graph y query."""
        if self.dashboard_graph_model == "ir.attachment":
            return "count(*)"
        elif self.dashboard_graph_model == "ir.attachment.type":
            return "count(*)"
        return super(DmsFolder, self)._graph_y_query()

    def _extra_sql_conditions(self):
        """More conditions for sql query."""
        return ""

    def _graph_title_and_key(self):
        """Return an array containing the appropriate graph
        title and key respectively."""
        return ["", ""]

    def _graph_data(self, start_date, end_date):
        """Return format should be an iterable of dicts that contain
        {'x_value': should either be dates, weeks, months, 'y_value': floats}."""
        query = """
        SELECT %(x_query)s as x_value, %(y_query)s as y_value
        FROM %(table)s
        WHERE folder_id = %(folder_id)s AND
          DATE(%(date_column)s) >= %(start_date)s AND
          DATE(%(date_column)s) <= %(end_date)s %(extra_conditions)s
        GROUP BY x_value;
        """
        # apply rules
        if not self.dashboard_graph_model:
            raise UserError(_("Undefined graph model for folder: %s") % self.name)
        graph_model = self.env["ir.attachment"]
        graph_table = graph_model._table
        extra_conditions = self._extra_sql_conditions()
        where_query = graph_model._where_calc([])
        graph_model.sudo()._apply_ir_rules(where_query, "read")
        (
            from_clause,
            where_clause,
            where_clause_params,
        ) = where_query.get_sql()
        if where_clause:
            extra_conditions += " AND " + where_clause

        query = query % {
            "x_query": self._graph_x_query(),
            "y_query": self._graph_y_query(),
            "table": graph_table,
            "folder_id": self.id,
            "date_column": self._graph_date_column(),
            "start_date": "'%s'" % start_date,
            "end_date": "'%s'" % end_date,
            "extra_conditions": extra_conditions,
        }
        self._cr.execute(query, [self.id, start_date, end_date] + where_clause_params)
        return self.env.cr.dictfetchall()

    def _get_graph(self):
        def get_week_name(start_date, locale):
            """Generate a week name (string) from a datetime according to the locale."""
            if (start_date + relativedelta(days=6)).month == start_date.month:
                short_name_from = format_date(start_date, "d", locale=locale)
            else:
                short_name_from = format_date(start_date, "d MMM", locale=locale)
            short_name_to = format_date(
                start_date + relativedelta(days=6), "d MMM", locale=locale
            )
            return short_name_from + "-" + short_name_to

        self.ensure_one()
        values = []
        today = fields.Date.from_string(fields.Date.context_today(self))
        start_date, end_date = self._graph_get_dates(today)
        graph_data = self._graph_data(start_date, end_date)
        # line graphs and bar graphs require different labels
        if self.dashboard_graph_type == "line":
            x_field = "x"
            y_field = "y"
        else:
            x_field = "label"
            y_field = "value"

        # generate all required x_fields and update the y_values
        # where we have data for them
        locale = self._context.get("lang") or "en_US"
        if self.dashboard_graph_group == "day":
            for day in range(0, (end_date - start_date).days + 1):
                short_name = format_date(
                    start_date + relativedelta(days=day), "d MMM", locale=locale
                )
                values.append({x_field: short_name, y_field: 0})
            for data_item in graph_data:
                index = (
                    datetime.strptime(str(data_item.get("x_value")), DATE_FORMAT).date()
                    - start_date
                ).days
                values[index][y_field] = data_item.get("y_value")

        elif self.dashboard_graph_group == "week":
            weeks_in_start_year = int(
                date(start_date.year, 12, 28).isocalendar()[1]
            )  # This date is always in the last week of ISO years
            for week in range(
                0,
                (end_date.isocalendar()[1] - start_date.isocalendar()[1])
                % weeks_in_start_year
                + 1,
            ):
                short_name = get_week_name(
                    start_date + relativedelta(days=7 * week), locale
                )
                values.append({x_field: short_name, y_field: 0})

            for data_item in graph_data:
                index = int(
                    (data_item.get("x_value") - start_date.isocalendar()[1])
                    % weeks_in_start_year
                )
                values[index][y_field] = data_item.get("y_value")

        elif self.dashboard_graph_group == "month":
            for month in range(0, (end_date.month - start_date.month) % 12 + 1):
                short_name = format_date(
                    start_date + relativedelta(months=month), "MMM", locale=locale
                )
                values.append({x_field: short_name, y_field: 0})

            for data_item in graph_data:
                index = int((data_item.get("x_value") - start_date.month) % 12)
                values[index][y_field] = data_item.get("y_value")
        else:
            for data_item in graph_data:
                values.append(
                    {
                        x_field: data_item.get("x_value"),
                        y_field: data_item.get("y_value"),
                    }
                )

        [graph_title, graph_key] = self._graph_title_and_key()
        color = "#875A7B" if "+e" in version else "#7c7bad"
        return [
            {
                "values": values,
                "area": True,
                "title": graph_title,
                "key": graph_key,
                "color": color,
            }
        ]
        
    @api.model
    def link_unlinked_attachments(self, *args, **kwargs):
        all_folders = self.search([])
        for folder in all_folders:
            # Assuming `documents_ids` is the field name for attachments linked to this folder
            unlinked_attachments = self.env['ir.attachment'].search([
                ('id', 'in', folder.documents_ids.ids),
                ('folder_id', '=', False)  # Or check for incorrect folder_id if necessary
            ])
            unlinked_attachments.write({'folder_id': folder.id})


class DmsScan(models.Model):
    _name = "dms.scan"
    _description = "scan"

    scan_documents = fields.Char(string="Scan documents", default=" ")


class DmsSearch(models.TransientModel):
    _name = "dms.search"
    _description = "search"

    name = fields.Char(string="Name")
    user_id = fields.Many2one(
        "res.users",
        string="Create by user",
        domain=lambda self: [
            "|",
            ("company_id", "=", False),
            ("company_id", "=", self.env.company.id),
        ],
    )
    code = fields.Char(string="Code")
    document_type_id = fields.Many2one("ir.attachment.type", string="Type")
    document_ids = fields.Many2many("ir.attachment", string="Documents")
    content = fields.Char(string="Content")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")

    def button_filter_search(self):
        """Change filter search."""
        domain = [
            ("res_model", "not in", ["ir.ui.view", "Country", "ir.ui.menu"]),
            ("res_field", "=", False),
            ("res_id", "=", False),
            ("create_uid", "not in", [1, 4]),
            ("extension", "not in", [".scss", ".ics", ".a"]),
        ]
        self.document_ids = False
        if self.name:
            domain = expression.AND([domain, [("name", "ilike", self.name)]])
        if self.user_id:
            domain = expression.AND([domain, [("create_uid", "=", self.user_id.id)]])
        if self.code:
            domain = expression.AND([domain, [("code", "=", self.code)]])
        if self.document_type_id:
            domain = expression.AND(
                [domain, [("type_id", "=", self.document_type_id.id)]]
            )
        if self.content:
            domain = expression.AND(
                [domain, [("index_content", "ilike", self.content)]]
            )
        if self.date_from and self.date_to:
            domain = expression.AND(
                [
                    domain,
                    [
                        ("create_date", ">=", str(self.date_from)),
                        ("create_date", "<=", str(self.date_to)),
                    ],
                ]
            )

        self.document_ids = self.env["ir.attachment"].search(domain).ids
