import base64
import logging

import werkzeug.utils
import werkzeug.wrappers

from odoo import _, http
from odoo.exceptions import AccessError
from odoo.http import request

_logger = logging.getLogger(__name__)


class DocumentController(http.Controller):
    @http.route("/dms/replace/document/<int:document_id>", type="http", auth="user")
    def replace(self, document_id, file, content_only=False, **kw):
        """Replace document."""
        record = request.env["ir.attachment"].browse([document_id])
        content = base64.b64encode(file.read())
        if file.store_fname == record.name or content_only:
            record.write({"datas": content})
        else:
            record.write({"name": file.store_fname, "datas": content})
        return werkzeug.wrappers.Response(status=200)

    @http.route("/dms/upload/document/<int:document_id>", type="http", auth="user")
    def upload(self, document_id, file, **kw):
        """Upload document."""
        record = request.env["dms.folder"].browse([document_id])
        content = base64.b64encode(file.read())
        request.env["ir.attachment"].create(
            {"name": file.store_fname, "parent_folder_id": record.id, "datas": content}
        )
        return werkzeug.wrappers.Response(status=200)

    @http.route(
        [
            "/dms/download/",
            "/dms/download/<int:document_id>",
            "/dms/download/<int:document_id>/<string:filename>",
            "/dms/download/<int:document_id>-<string:unique>",
            "/dms/download/<int:document_id>-<string:unique>/<string:filename>",
        ],
        type="http",
        auth="user",
    )
    def download(
        self, document_id=None, filename=None, unique=None, data=None, token=None, **kw
    ):
        """Download document."""
        status, headers, content = request.registry["ir.http"].binary_content(
            model="ir.attachment",
            id=document_id,
            field="datas",
            unique=unique,
            filename=filename,
            filename_field="name",
            download=True,
        )
        if status == 304:
            response = werkzeug.wrappers.Response(status=status, headers=headers)
        elif status == 301:
            return werkzeug.utils.redirect(content, code=301)
        elif status != 200:
            response = request.not_found()
        else:
            content_base64 = base64.b64decode(content)
            headers.append(("Content-Length", len(content_base64)))
            response = request.make_response(content_base64, headers)
        if token:
            response.set_cookie("fileToken", token)
        return response

    @http.route(
        [
            "/dms/checkout/",
            "/dms/checkout/<int:document_id>",
            "/dms/checkout/<int:document_id>/<string:filename>",
            "/dms/checkout/<int:document_id>-<string:unique>",
            "/dms/checkout/<int:document_id>-<string:unique>/<string:filename>",
        ],
        type="http",
        auth="user",
    )
    def checkout(
        self, document_id=None, filename=None, unique=None, data=None, token=None, **kw
    ):
        """Checkout document."""
        status, headers, content = request.registry["ir.http"].binary_content(
            model="ir.attachment",
            id=document_id,
            field="datas",
            unique=unique,
            filename=filename,
            filename_field="name",
            download=True,
        )
        if status == 304:
            response = werkzeug.wrappers.Response(status=status, headers=headers)
        elif status == 301:
            return werkzeug.utils.redirect(content, code=301)
        elif status != 200:
            response = request.not_found()
        else:
            content_base64 = base64.b64decode(content)
            headers.append(("Content-Length", len(content_base64)))
            response = request.make_response(content_base64, headers)
        if token:
            response.set_cookie("fileToken", token)
        try:
            lock = request.env["ir.attachment"].browse(id).user_lock()[0]
            response.set_cookie("checkoutToken", lock["token"])
        except AccessError:
            response = werkzeug.exceptions.Forbidden()
        return response

    @http.route("/dms/checkin/", type="http", auth="user")
    def checkin(self, ufile, token=None, **kw):
        """Checkin document."""
        file_token = request.httprequest.headers.get("token") or token
        if not file_token:
            return werkzeug.exceptions.Forbidden()
        lock = (
            request.env["muk_security.lock"]
            .sudo()
            .search([("token", "=", file_token)], limit=1)
        )
        refrence = lock.lock_ref
        if refrence._name == "ir.attachment":
            lock.unlink()
            data = ufile.read()
            filename = ufile.filename
            refrence.write({"datas": base64.b64encode(data), "name": filename})
            return werkzeug.wrappers.Response(status=200)
        else:
            return werkzeug.exceptions.Forbidden()

    @http.route("/config/muk_dms.max_upload_size", type="json", auth="user")
    def max_upload_size(self, **kw):
        """Set max upload size."""
        params = request.env["ir.config_parameter"].sudo()
        return {
            "max_upload_size": int(
                params.get_param("muk_dms.max_upload_size", default=25)
            )
        }

    @http.route("/config/muk_dms.forbidden_extensions", type="json", auth="user")
    def forbidden_extensions(self, **kw):
        """Set forbidden extensions."""
        params = request.env["ir.config_parameter"].sudo()
        return {
            "forbidden_extensions": params.get_param(
                "muk_dms.forbidden_extensions", default=""
            )
        }

    @http.route("/tree/create/folder", type="json", auth="user")
    def create_directory(self, parent_directory, name=None, context=None, **kw):
        """Create new folder."""
        parent = request.env["dms.folder"].sudo().browse(parent_directory)
        uname = parent.unique_name(
            name or _("New Directory"), parent.child_directories.mapped("name")
        )
        directory = (
            request.env["dms.folder"]
            .with_context(context or request.env.context)
            .create({"name": uname, "parent_folder_id": parent_directory})
        )
        return {
            "id": "directory_%s" % directory.id,
            "text": directory.name,
            "icon": "fa fa-folder-o",
            "type": "directory",
            "data": {
                "odoo_id": directory.id,
                "odoo_model": "dms.folder",
                "odoo_record": False,
                "name": directory.name,
                "child_ids": directory.count_directories,
                "documents_ids": directory.count_files,
                "parent_folder_id": "directory_%s" % parent_directory,
            },
            "children": False,
        }
