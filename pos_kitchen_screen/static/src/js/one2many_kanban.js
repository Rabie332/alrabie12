odoo.define("mrp_plm.update_kanban", function (require) {
    "use strict";

    var KanbanRecord = require("web.KanbanRecord");

    KanbanRecord.include({
        _get_M2M_data: function (field) {
            var lines = [];
            if (field in this.recordData && this.recordData[field].data) {
                lines = this.recordData.lines.data;
            }
            return lines;
        },
        _setState: function (recordState) {
            var self = this;
            this._super(recordState);
            self.qweb_context.get_m2m_data = self._get_M2M_data.bind(self);
        },
    });
});
