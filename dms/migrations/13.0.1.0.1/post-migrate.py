def migrate(cr, version):
    """Update filed parent id max in dms folder."""
    cr.execute("UPDATE dms_folder  SET parent_folder_id = temporary_parent_folder_id ")
    # Drop temporary column
    cr.execute("ALTER TABLE dms_folder DROP COLUMN temporary_parent_folder_id")
