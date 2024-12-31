from odoo import api, models

class TransportationRequestReport(models.AbstractModel):
    _name = "report.transportation_reports.transportation_request_report"
    _description = "Transportation Request Report"

    def _get_lines(self, records, transport_type):
        result = []
        for record in records:
            line_data = {
                'id': record.id,
                'name': record.name,
                'partner': record.partner_id.name,
                'shipping_number': record.shipping_number,
                'number_shipment': record.number_shipment,
                'shipment_type_line_ids': [
                    {'shipment_type_size_name': line.shipment_type_size_id.name}
                    for line in record.shipment_type_line_ids
                ],
                'order_ids': [{
                    'line_ids': [{
                        'delivery_date': line.delivery_date,
                        'create_date': line.create_date
                    } for line in order.line_ids]
                } for order in record.order_ids],
                'state': record.state,
                'last_date_empty_container': record.last_date_empty_container,
                'containers': [],
                
            }

            if transport_type == "port":
                for statement_line in record.statement_line_ids:
                    if statement_line.container_number not in record.order_ids.mapped('line_ids.container_number'):
                        line_data['containers'].append(statement_line.container_number)
            elif transport_type == "warehouse":
                warehouse_containers = set()
                customer_containers = set()

                for shipping_order in record.order_ids:
                    if shipping_order.transport_type == "warehouse":
                        for shipping_order_line in shipping_order.line_ids:
                            warehouse_containers.add(shipping_order_line.goods_id.container_number)
                    elif shipping_order.transport_type == "customer":
                        for shipping_order_line in shipping_order.line_ids:
                            customer_containers.add(shipping_order_line.goods_id.container_number)

                line_data['containers'] = list(warehouse_containers - customer_containers)
            else:
                for shipping_order in record.order_ids:
                    if shipping_order.transport_type == transport_type:
                        for shipping_order_line in shipping_order.line_ids:
                            line_data['containers'].append(shipping_order_line.goods_id.container_number)

            result.append(line_data)

        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        ids = data.get("ids", [])
        docs = self.env["transportation.request.wizard"].browse(docids)
        clearance_records = self.env[data['model']].browse(ids)
        transport_type = data['form']['transport_type']
        lines = self._get_lines(clearance_records, transport_type)

        return {
            "doc_ids": docids,
            "doc_model": "transportation.request.wizard",
            "docs": docs,
            "lines": lines,
        }
