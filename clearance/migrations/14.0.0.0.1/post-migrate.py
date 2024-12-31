def migrate(cr, version):
    """Update supplier name of clearance request invoice."""
    cr.execute(
        "UPDATE clearance_request_invoice SET supplier_name=temporary_supplier_name"
    )
    # Drop temporary column
    cr.execute(
        "ALTER TABLE clearance_request_invoice DROP COLUMN temporary_supplier_name"
    )
