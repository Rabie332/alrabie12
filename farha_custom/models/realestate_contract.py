from datetime import date

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    contract_id = fields.Many2one("realestate.contract", string="Contract")
    contract_line_id = fields.Many2one(
        "realestate.contract.line", string="Contract line"
    )


class InstallmentTemplate(models.Model):
    _inherit = "installment.template"

    product_id = fields.Many2one("product.product", string="Product")


class RealestateContractLine(models.Model):
    _inherit = "realestate.contract.line"

    invoice_id = fields.Many2one("account.move", string="Invoice")


class RealestateContractService(models.Model):
    _name = "realestate.contract.service"
    _description = "Realestate Contract Service"

    name = fields.Char(string="Name")
    amount = fields.Float(string="Amount")
    contract_id = fields.Many2one("realestate.contract", string="Contract")


class RealestateContract(models.Model):
    _inherit = "realestate.contract"

    unified_contract_number = fields.Char(string="Unified Contract Number")
    attachment_count = fields.Integer(
        string="Attachments number",
        compute="_compute_attachment_count",
    )
    services_ids = fields.One2many(
        "realestate.contract.service", "contract_id", string="services"
    )
    invoice_ids = fields.One2many("account.move", "contract_id", string="Invoices")
    invoices_count = fields.Integer(
        compute="_compute_invoices_count", string="Contract Count"
    )

    def _compute_invoices_count(self):
        for contract in self:
            contract.invoices_count = len(contract.invoice_ids)

    def action_view_invoice(self):
        """Return view of invoice corresponding to the current contract"""
        action = super(RealestateContract, self).action_view_invoice()
        action["domain"] = [
            "|",
            ("id", "in", self.invoice_ids.ids),
            ("id", "=", self.invoice_id.id),
        ]
        return action

    def _compute_attachment_count(self):
        for contract in self:
            contract.attachment_count = contract.env["ir.attachment"].search_count(
                [("res_model", "=", contract._name), ("res_id", "in", contract.ids)]
            )

    def attachment_tree_view(self):
        """Get attachments for Contract."""
        attachment_action = self.env.ref("base.action_attachment")
        action = attachment_action.sudo().read()[0]
        action["context"] = {
            "default_res_model": "realestate.contract",
            "default_res_id": self.ids[0],
        }
        action["domain"] = str(
            ["&", ("res_model", "=", self._name), ("res_id", "in", self.ids)]
        )
        return action

    @api.model
    def create_invoice_installment(self):
        """Get all installments of today and who are confirmed"""

        for installment in self.env["realestate.contract.line"].search(
            [
                ("contract_id.state", "=", "confirmed"),
                ("date", "<=", date.today()),
                ("invoice_id", "=", False),
                ("contract_id.invoice_id", "=", False),
                ("contract_id.template_id.product_id", "!=", False),
            ]
        ):
            installment.contract_id.create_installment_invoice(
                installment.contract_id, installment
            )

    def prepare_invoice_lines_vals(self, contract, installment):
        """Prepare invoice line values"""
        invoice_line_ids = [
            (
                0,
                0,
                {
                    "quantity": 1,
                    "price_unit": installment.amount,
                    "product_id": contract.template_id.product_id.id,
                    "name": (_("Rent of  installment {} of period {} to {}")).format(
                        contract.name,
                        str(installment.date),
                        str(
                            contract.add_months(
                                installment.date, contract.template_id.repetition_rate
                            )
                        ),
                    ),
                },
            )
        ]
        for service in contract.services_ids:
            # add services  to invoice line
            invoice_line_ids.append(
                (
                    0,
                    0,
                    {
                        "quantity": 1,
                        "price_unit": service.amount / len(contract.contract_line_ids),
                        "name": service.name,
                    },
                )
            )
        return invoice_line_ids

    def create_installment_invoice(self, contract, installment):
        """Prepare invoice values then create it"""
        fiscal_position = (
            contract.env["account.fiscal.position"]
            .with_company(contract.company_id)
            .get_fiscal_position(contract.partner_id.id, delivery_id=None)
        )
        # create invoice
        invoice = self.env["account.move"].create(
            {
                "contract_id": contract.id,
                "ref": contract.name,
                "invoice_origin": contract.name,
                "move_type": "out_invoice",
                "partner_id": contract.partner_id.id,
                "invoice_date": installment.date,
                "invoice_line_ids": self.prepare_invoice_lines_vals(
                    contract, installment
                ),
                "company_id": contract.company_id.id,
                "fiscal_position_id": fiscal_position,
                "currency_id": contract.company_id.currency_id.id,
                "invoice_payment_term_id": contract.partner_id.property_payment_term_id,
                "journal_id": contract.env["account.journal"]
                .search(
                    [
                        ("company_id", "=", contract.company_id.id),
                        ("type", "=", "sale"),
                    ],
                    limit=1,
                )
                .id,
            }
        )
        # update invoice lines
        for line in invoice.invoice_line_ids:
            price = line.price_unit
            description = line.name
            line.with_context(check_move_validity=False)._onchange_product_id()
            line.with_context(
                check_move_validity=False
            )._onchange_product_id_account_invoice_pricelist()
            line.with_context(check_move_validity=False)._onchange_uom_id()
            line.with_context(check_move_validity=False).price_unit = price
            line.with_context(check_move_validity=False).name = description
        invoice.with_context(check_move_validity=False)._onchange_invoice_line_ids()
        invoice.with_context(check_move_validity=False)._recompute_tax_lines()
        # affect invoice to installment to avoid the creation
        # of more than one invoice for each installment
        installment.invoice_id = invoice.id
