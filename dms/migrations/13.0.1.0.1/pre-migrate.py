def migrate(cr, version):
    """Update filed parent id max in dms folder."""
    cr.execute("ALTER TABLE dms_folder ADD temporary_parent_folder_id int")
    cr.execute("UPDATE dms_folder SET temporary_parent_folder_id = parent_id ")
