# pylint: disable=invalid-name,wrong-import-order
import datetime

from .common import OvertimeCommon


class TestOvertimeMandateFlow(OvertimeCommon):
    def test_overtime_mandate_flow(self):  # pylint: disable=too-many-locals

        """Test overtime mandate Workflow."""

        # I create a new employee "Richard"
        self.richard_emp = self.env["hr.employee"].create(
            {
                "name": "Richard",
                "gender": "male",
                "birthday": "1984-05-01",
                "country_id": self.ref("base.be"),
                "department_id": self.ref("hr.dep_rd"),
            }
        )
        overtime_mandate = self.env["hr.overtime.mandate"].create({"name": "0007"})

        self.env["hr.overtime.mandate.line"].create(
            {
                "overtime_mandate_id": overtime_mandate.id,
                "employee_id": self.richard_emp.id,
                "mission": "Task 01",
                "date_from": datetime.datetime.now() - datetime.timedelta(days=1),
                "date_to": datetime.datetime.now(),
                "hour_number": 5,
            }
        )
        # check request has the right stage and state

        self.assertEqual(overtime_mandate.stage_id.name, "Send")
        self.assertEqual(overtime_mandate.state, "draft")

        # accept request by user_manager

        overtime_mandate.with_user(self.user_manager).action_accept()
