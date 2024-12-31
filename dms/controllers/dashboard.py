import logging
from datetime import datetime

from odoo import _, fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class DashboardController(http.Controller):
    @http.route("/dms/fetch_dashboard_data", type="json", auth="user")
    def fetch_dashboard_dms_data(
        self, date_from, date_to, date_from_calendar, date_to_calendar
    ):
        """Fetch Data."""
        dms_folder_obj = request.env["dms.folder"]
        dms_cabinet_obj = request.env["dms.cabinet"]
        dms_document_obj = request.env["ir.attachment"]
        # smart buttons
        domain_filter = [
            ("create_date", ">=", date_from),
            ("create_date", "<=", date_to),
        ]
        if date_from_calendar and date_to_calendar:
            domain_filter = [
                ("create_date", ">=", date_from_calendar),
                ("create_date", "<=", date_to_calendar),
            ]
        folders_count = dms_folder_obj.search_count(domain_filter)
        cabinets_count = dms_cabinet_obj.search_count(domain_filter)
        documents_count = dms_document_obj.search_count(
            [
                ("res_model", "not in", ["ir.ui.view", "Country", "ir.ui.menu"]),
                ("res_field", "=", False),
                ("res_id", "=", False),
                ("create_uid", "not in", [1, 4]),
                ("extension", "not in", [".scss", ".ics", ".a"]),
            ]
            + domain_filter
        )

        # last_documents
        last_documents = dms_document_obj.search(
            [
                ("res_model", "not in", ["ir.ui.view", "Country", "ir.ui.menu"]),
                ("res_field", "=", False),
                ("res_id", "=", False),
                ("create_uid", "not in", [1, 4]),
                ("extension", "not in", [".scss", ".ics", ".a"]),
            ]
            + domain_filter,
            limit=10,
        )
        url = (
            request.env["ir.config_parameter"]
            .sudo()
            .search([("key", "=", "web.base.url")], limit=1)
            .value
        )
        documents_last = []
        if last_documents:
            for last_document in last_documents:
                if last_document.extension in [
                    ".jpg",
                    ".png",
                    ".jpeg",
                    ".jfif",
                    ".gif",
                    ".tiff",
                    ".exif",
                    ".bmp",
                    ".webp",
                    ".bat",
                    ".bpg",
                    ".svg",
                    ".ppm",
                    ".pgm",
                    ".pbm",
                    ".pnm",
                    ".tif",
                    ".jls",
                    ".jp2",
                    ".jpe",
                    ".j2k",
                    ".jpf",
                    ".jpx",
                    ".jpm",
                    ".mj2",
                    ".psd",
                    ".eps",
                    ".epsf",
                    ".ai",
                    ".swf",
                    ".pct",
                    ".odg",
                ]:
                    icon = "fa fa-file-image-o fa-3x"
                elif last_document.extension in [".pdf"]:
                    icon = "fa fa-file-pdf-o fa-3x"
                elif last_document.extension in [".doc", ".docx", ".wiz"]:
                    icon = "fa fa-file-word-o fa-3x"
                elif last_document.extension in [".ppt", ".pptx", ".pwz"]:
                    icon = "fa fa-file-powerpoint-o fa-3x"
                elif last_document.extension in [".xlsx"]:
                    icon = "fa fa-file-excel-o fa-3x"
                elif last_document.extension in [".css", ".js", ".html"]:
                    icon = "fa fa-file-code-o fa-3x"
                else:
                    icon = "fa fa-file fa-3x"
                details_url = "{}/web#id={}&view_type=form&model={}".format(
                    url, last_document.id, last_document._name
                )
                documents_last.append(
                    {
                        "name": last_document.name,
                        "description": last_document.description,
                        "date": last_document.create_date,
                        "user": last_document.create_uid.name,
                        "icon": icon,
                        "details_url": details_url,
                    }
                )

        # Graph : Documents by type
        documents_by_type = []
        dms_type = []
        all_types = request.env["ir.attachment.type"].search([])
        for attachment_type in all_types:
            type_count = dms_document_obj.search_count(
                [("type_id", "=", attachment_type.id)]
                + [
                    ("res_model", "not in", ["ir.ui.view", "Country", "ir.ui.menu"]),
                    ("res_field", "=", False),
                    ("res_id", "=", False),
                    ("create_uid", "not in", [1, 4]),
                    ("extension", "not in", [".scss", ".ics", ".a"]),
                ]
                + domain_filter
            )
            documents_by_type.append(type_count)
            dms_type.append(attachment_type.name)

        # Graph : Documents flow
        labels = []
        document_data = []

        MONTH_NAMES = {
            1: _("January"),
            2: _("February"),
            3: _("March"),
            4: _("April"),
            5: _("May"),
            6: _("June"),
            7: _("July"),
            8: _("August"),
            9: _("September"),
            10: _("October"),
            11: _("November"),
            12: _("December"),
        }

        day_name = {
            0: _("Monday"),
            1: _("Tuesday"),
            2: _("Wednesday"),
            3: _("Thursday"),
            4: _("Friday"),
            5: _("Saturday"),
            6: _("Sunday"),
        }

        week_name = {
            1: _("Week 1"),
            2: _("Week 2"),
            3: _("Week 3"),
            4: _("Week 4"),
            5: " ",
        }

        number_days = (
            datetime.strptime(date_to, "%Y-%m-%d")
            - datetime.strptime(date_from, "%Y-%m-%d")
        ).days + 1
        if date_from_calendar and date_to_calendar:
            number_days = (
                datetime.strptime(date_to_calendar, "%Y-%m-%d")
                - datetime.strptime(date_from_calendar, "%Y-%m-%d")
            ).days + 1
        documents = dms_document_obj.search(
            [
                ("res_model", "not in", ["ir.ui.view", "Country", "ir.ui.menu"]),
                ("res_field", "=", False),
                ("res_id", "=", False),
                ("create_uid", "not in", [1, 4]),
                ("extension", "not in", [".scss", ".ics", ".a"]),
            ]
            + domain_filter
        )
        if number_days <= 1:
            day_number = fields.Date.from_string(date_from).weekday()
            labels.append(day_name[int(day_number)])
            document_data.append(len(documents))
        elif 1 < number_days <= 7:
            for day in range(0, 7):
                labels.append(day_name[day])
                document_data.append(
                    len(
                        documents.filtered(
                            lambda rec: fields.Date.from_string(
                                rec.create_date
                            ).weekday()
                            == day
                        )
                    )
                )
        elif 7 < number_days <= 31:
            for week in range(1, (number_days // 7 + 1) + 1):
                labels.append(week_name[week])
                document_data.append(
                    len(
                        documents.filtered(
                            lambda rec: (fields.Date.from_string(rec.create_date).day)
                            // 7
                            + 1
                            == week
                        )
                    )
                )
        elif number_days > 31:
            for month in range(1, 13):
                labels.append(MONTH_NAMES[month])
                document_data.append(
                    len(
                        documents.filtered(
                            lambda rec: fields.Date.from_string(rec.create_date).month
                            == month
                        )
                    )
                )

        # Graph : Folders by tags
        all_tags = request.env["dms.tag"].search([])
        dms_tags = []
        folders_by_tag = []
        for tag in all_tags:
            count = dms_folder_obj.search_count(
                [("tag_ids", "in", tag.id)] + domain_filter
            )
            if count:
                dms_tags.append(tag.name)
                folders_by_tag.append(count)

        # Graph :Documents by extensions
        extensions_document = []
        extensions = []
        percent_extension = []

        for document in documents:
            if document.extension:
                extensions_document.append(document.extension)
        extensions_document = set(extensions_document)

        extensions = list(extensions_document)

        for extension in extensions:
            document_count = dms_document_obj.search_count(
                [("extension", "=", extension)]
                + [
                    ("res_model", "not in", ["ir.ui.view", "Country", "ir.ui.menu"]),
                    ("res_field", "=", False),
                    ("res_id", "=", False),
                    ("create_uid", "not in", [1, 4]),
                    ("extension", "not in", [".scss", ".ics", ".a"]),
                ]
                + domain_filter
            )
            percent_extension.append(
                format(float(document_count) * 100 / (len(documents) or 1.0), ".2f")
            )
        if len(percent_extension) >= 5:
            percent_extension = percent_extension[:5]

        # Calculate the size of all documents
        documents = dms_document_obj.search(
            [
                ("res_model", "not in", ["ir.ui.view", "Country", "ir.ui.menu"]),
                ("res_field", "=", False),
                ("res_id", "=", False),
                ("create_uid", "not in", [1, 4]),
                ("extension", "not in", [".scss", ".ics", ".a"]),
            ]
            + domain_filter
        )
        documents_size = 0
        for document in documents:
            documents_size += document.file_size
        if documents_size:
            documents_size = round(documents_size / 1000000, 1)

        # Graph : Documents  by folder
        all_folder = dms_folder_obj.search([], limit=10)
        dms_folder = []
        documents_by_folder = []
        for folder in all_folder:
            documents_by_folder_count = folder.documents_count
            if documents_by_folder_count:
                dms_folder.append(folder.name)
                documents_by_folder.append(documents_by_folder_count)
        return {
            "data": {
                "documents_last": documents_last,
                "folders_by_tag": folders_by_tag,
                "dms_tags": dms_tags,
                "dms_type": dms_type,
                "documents_by_type": documents_by_type,
                "document_data": document_data,
                "labels": labels,
                "percent_extension": percent_extension,
                "extensions": extensions,
                "dms_folder": dms_folder,
                "documents_by_folder": documents_by_folder,
            },
            "smart_buttons": [
                {
                    "name": _("Documents number"),
                    "value": documents_count,
                    "action_name": "dms.ir_attachment_action",
                    "icon": "fa fa-file ",
                    "color_class": "bg-green",
                },
                {
                    "name": _("Folders number"),
                    "value": folders_count,
                    "action_name": "dms.dms_folder_action_all_folders",
                    "icon": "fa fa-folder ",
                    "color_class": "bg-yellow",
                },
                {
                    "name": _("Cabinets number"),
                    "value": cabinets_count,
                    "action_name": "dms.action_dms_cabinet",
                    "icon": "fa fa-archive",
                    "color_class": "bg-red",
                },
                {
                    "name": _("Documents size"),
                    "value": "MB " + str(documents_size),
                    "action_name": "dms.ir_attachment_action",
                    "icon": "fa fa-hdd-o",
                    "color_class": "bg-aqua",
                },
            ],
        }
