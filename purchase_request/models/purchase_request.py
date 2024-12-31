from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _description = "Purchase Request"
    _inherit = ["request"]

    estimated_budget = fields.Float(
        string="Estimated budget",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    description = fields.Text(
        string="Description",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    reason = fields.Text(
        string="Reason", readonly=1, states={"draft": [("readonly", 0)]}
    )
    active = fields.Boolean(default=True)
    line_ids = fields.One2many(
        "purchase.request.line",
        "purchase_request_id",
        string="Products",
    )
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")

    duration_expected = fields.Float(
        string="Expected duration (days)",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    category_id = fields.Many2one(
        "purchase.request.category",
        string="Category",
        readonly=1,
    )
    account_id = fields.Many2one(
        "purchase.request.account",
        string="Account",
        readonly=1,
    )
    account_description = fields.Text(string="Account description", readonly=1)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )

    @api.model
    def create(self, vals):
        """Add sequence."""
        purchase = super(PurchaseRequest, self).create(vals)
        if purchase:
            purchase.name = self.env["ir.sequence"].next_by_code("purchase.request.seq")
            for attachment in purchase.attachment_ids.filtered(
                lambda attachment: not attachment.res_id
            ):
                attachment.res_id = purchase.id
        return purchase

    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)
        for attachment in self.attachment_ids.filtered(
            lambda attachment: not attachment.res_id
        ):
            attachment.res_id = self.id
        return res

    @api.constrains("request_type_id", "estimated_budget")
    def _check_type(self):
        """Check estimated budget."""
        for purchase in self:
            if (
                purchase.request_type_id
                and purchase.estimated_budget
                and purchase.request_type_id.budget_max > 0
                and (
                    purchase.request_type_id.budget_max < purchase.estimated_budget
                    or purchase.estimated_budget < purchase.request_type_id.budget_min
                )
            ):
                raise ValidationError(
                    _("Estimated budget should be between %s and %s")
                    % (
                        purchase.request_type_id.budget_min,
                        purchase.request_type_id.budget_max,
                    )
                )

    def action_send(self):
        """Send the request to be approved by the right users."""
        for request in self:
            if not request.line_ids:
                raise ValidationError(_("You should choose products"))
            if request.estimated_budget <= 0:
                raise ValidationError(_("Estimated budget should be greater than 0"))
            for line in request.line_ids:
                if line.product_qty <= 0:
                    raise ValidationError(
                        _("The quantity of the product")
                        + line.product_id.name
                        + _("must be greater than zero")
                    )
            return super(PurchaseRequest, self).action_send()

    @api.onchange("category_id")
    def _onchange_category(self):
        if self.category_id:
            self.account_id = False

    def _sync_employee_details(self):
        for request in self:
            super(PurchaseRequest, request)._sync_employee_details()
            request.company_id = request.employee_id.company_id.id

    def name_get(self):
        result = []
        for record in self:
            name = "PR%s " % (record.name)
            result.append((record.id, name))
        return result


class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"
    _description = "Purchase Request Line"

    purchase_request_id = fields.Many2one("purchase.request", string="Purchase")
    is_editable = fields.Boolean(compute='_compute_is_editable')

    @api.depends('purchase_request_id.state')
    def _compute_is_editable(self):
        for line in self:
            line.is_editable = line.purchase_request_id.state == 'draft'
            
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain=[("purchase_ok", "=", True)],
        required=1,
    )
    product_qty = fields.Float(
        string="Quantity", digits="Product Unit of Measure", required=1
    )
    notes = fields.Text(string="Notes")
    company_id = fields.Many2one(
        "res.company",
        related="purchase_request_id.company_id",
        string="Company",
        copy=False,
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Product Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]",
        readonly=1,
    )
    product_uom_category_id = fields.Many2one(
        string="Product Category", related="product_id.uom_id.category_id"
    )
    description = fields.Text(string="Description")

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """Get unity from product."""
        if self.product_id:
            self.product_uom_id = self.product_id.uom_po_id.id
            self.description = self.product_id.display_name

class PurchaseRequestType(models.Model):
    _inherit = "request.type"

    budget_max = fields.Float(string="Budget Maximum")
    budget_min = fields.Float(string="Budget Minimum")
    is_committee_required = fields.Boolean(string="Committee Required")


class PurchaseRequestCategory(models.Model):
    _name = "purchase.request.category"
    _description = "Categories"

    name = fields.Char(string="Name", required=1)


class PurchaseRequestAccount(models.Model):
    _name = "purchase.request.account"
    _description = "Accounts"

    name = fields.Char(string="Name", required=1)
    category_id = fields.Many2one(
        "purchase.request.category", string="Category", required=1
    )
