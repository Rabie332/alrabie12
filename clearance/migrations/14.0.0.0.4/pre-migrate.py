def migrate(cr, version):
    """Save insurance from clearance goods definition in new column ."""
    cr.execute("ALTER TABLE clearance_goods_definition ADD temporary_insurance varchar")
    cr.execute("UPDATE clearance_goods_definition SET temporary_insurance = insurance")
