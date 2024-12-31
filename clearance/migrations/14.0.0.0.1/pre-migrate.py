def migrate(cr, version):
    """Save supplier name from supplier in new column ."""
    cr.execute(
        "ALTER TABLE clearance_request_invoice ADD temporary_supplier_name varchar"
    )
    cr.execute(
        "UPDATE clearance_request_invoice SET temporary_supplier_name "
        "= (SELECT name FROM res_partner where id=supplier_id)"
    )
