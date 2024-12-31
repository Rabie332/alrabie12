from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalAccount(CustomerPortal):
    # Display only posted invoices
    def _get_invoices_domain(self):
        return [
            (
                "move_type",
                "in",
                (
                    "out_invoice",
                    "out_refund",
                    "in_invoice",
                    "in_refund",
                    "out_receipt",
                    "in_receipt",
                ),
            ),
            ("state", "=", "posted"),
        ]
