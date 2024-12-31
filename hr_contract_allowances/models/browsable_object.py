class BrowsableObject(object):
    def __init__(self, employee_id, args, env):
        self.employee_id = employee_id
        self.dict = args
        self.env = env

    def __getattr__(self, attr):
        return attr in self.dict and self.dict.__getitem__(attr) or 0.0


class AllowanceLine(BrowsableObject):
    """a class that will be used into the python code, mainly for usability purposes"""

    def sum(self, code):
        self.env.cr.execute(
            """
            SELECT sum(amount) as sum
            FROM hr_contrat as hc, hr_contract_allowance_line as hca
            WHERE hc.employee_id = %s AND hc.state = 'done'
            AND hc.id = hca.contract_id AND hca.allowance_id.code = %s""",
            (self.employee_id, code),
        )
        return self.env.cr.fetchone()[0] or 0.0
