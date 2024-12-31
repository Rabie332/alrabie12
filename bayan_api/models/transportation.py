from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import requests
import base64
import json
from datetime import datetime, timedelta
import re


class ShippingOrder(models.Model):
    _inherit = "shipping.order"
    line_ids = fields.One2many(
        "shipping.order.line",
        "shipping_order_id",
        string="Shipping Order Line",
        readonly=True,
        states={"draft": [("readonly", False)], "done": [("readonly", False)]},
    )
    
    def action_view_attachments(self):
        order_line_ids = self.line_ids.ids  # Assuming `line_ids` is a One2many field to `shipping.order.line`
        domain = [
                "|",
                "&",
                ("res_model", "=", self._name),
                ("res_id", "in", self.ids),
                "&",
                ("res_model", "=", self.line_ids._name),
                ("res_id", "in", order_line_ids),
            ]
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Attachments'),
            'view_mode': 'tree,form',
            'res_model': 'ir.attachment',
            'domain': domain,
            'context': {
                    "default_res_model": "shipping.order",
                    "default_res_id": self.ids[0],
                }
        }
        
        
   
class ShippingOrderLine(models.Model):
    _inherit = 'shipping.order.line'
    waybill_id = fields.Integer(string="Waybill ID")
    trip_id = fields.Integer(string="Trip ID")
    print_way_bill_report_done = fields.Boolean("Confirmed", default=False)
    goods_id = fields.Many2one("clearance.request.shipment.type", string="Good")
    
    # This field will display the Bayan goods type related to the selected good
    goods_types_id_bayan = fields.Many2one("goods.type", string="Bayan Goods Type", compute="_compute_goods_type", store=True, readonly=False)

    @api.depends('goods_id.goods_type_bayan')
    def _compute_goods_type(self):
        for record in self:
            record.goods_types_id_bayan = record.goods_id.goods_type_bayan.id if record.goods_id else False
            
            
    def create_waybill_bayan(self):
        license_plate = self.vehicle_id.license_plate
        plate_dict = self._convert_vehicle_plate_to_dict(license_plate)
        data, headers = self._prepare_waybill_data(plate_dict)
        return self._send_waybill_request(data, headers)

    def _convert_vehicle_plate_to_dict(self, plate):
        english_to_arabic = {
            'A': 'ا', 'B': 'ب', 'J': 'ح', 'D': 'د', 'R': 'ر', 'S': 'س',
            'X': 'ص', 'T': 'ط', 'E': 'ع', 'G': 'ق', 'K': 'ك', 'L': 'ل',
            'Z': 'م', 'N': 'ن', 'H': 'هـ', 'U': 'و', 'V': 'ى'
        }
        parts = plate.split()
        alphabetic_part, numeric_part = parts[0], parts[1]
        arabic_letters = [english_to_arabic[char] for char in alphabetic_part]
        return {
            "leftLetter": arabic_letters[0],
            "middleLetter": arabic_letters[1],
            "rightLetter": arabic_letters[2],
            "number": numeric_part
        }
 
    def format_mobile_number(self, mobile):
        """
        Takes a mobile number as input and formats it by removing spaces and the plus sign.
        
        :param mobile: The mobile number to format.
        :return: Formatted mobile number without spaces and plus sign.
        """
        if mobile:
            # Remove spaces and plus sign
            formatted_mobile = mobile.replace(' ', '').replace('+', '')
            return formatted_mobile
        return mobile
    
    def _prepare_waybill_data(self, plate_dict):
        app_id, app_key, client_id = self._get_api_credentials()
        phone_number = self.shipping_order_id.partner_id.phone
        phone = phone_number.replace(" ", "")
        driver_name_raw = self.driver_id.name
        # Regular expression to find trailing digits
        pattern = re.compile(r'\d+$')

        # Check if the name ends with digits (indicating an ID is present)
        if pattern.search(driver_name_raw):
            # If digits are found, remove them to isolate the name
            driver_name_cleaned = pattern.sub('', driver_name_raw).strip()
            # Indicates the name and ID were present
            has_id = True
        else:
            # If no digits are found at the end, the name is already clean
            driver_name_cleaned = driver_name_raw
            # Indicates the name was present without an appended ID
            has_id = False

        # Ensure that receivedDate is within 3 days from today
        if self.delivery_date:
            received_date = self.delivery_date
        else:
            # Handle the case where delivery_date is not set
            # For example, default to today's date or any other logic you deem appropriate
            received_date = datetime.now().date()

        # Set expectedDeliveryDate to 6 days after received_date
        expected_delivery_date = received_date + timedelta(days=5)

        # Format dates for the API request
        formatted_received_date = received_date.strftime('%Y-%m-%d')
        formatted_expected_delivery_date = expected_delivery_date.strftime('%Y-%m-%d')
        
        dangerous_codes = [36, 37, 38, 39, 40, 41, 42, 43, 44]
        goods_id_bayan = self.goods_id.goods_type_bayan.goods_id_bayan

        # Initialize the item with fields that are always present
        item = {
            "unitId": 5,
            "valid": True,
            "quantity": 1,
            "goodTypeId": goods_id_bayan,
            "weight": self.weight or '20000'
        }

        # Conditionally add the dangerousCode field only for dangerous goods
        if goods_id_bayan in dangerous_codes:
            item["dangerousCode"] = "Yes"
            

        delivery_location = {
            "countryCode": "SA",
            "address": self.shipment_to, 
        }

        route_name = self.route_id.name
        qatar_routes = ['Dammam-Qatar', 'Dammam-Qatar - Lowbed']

        # Conditionally add cityId if not a route to Qatar
        if route_name not in qatar_routes:
            # This ensures cityId is only added if the route is not to Qatar
            delivery_location["cityId"] = self.route_id.bayan_route_to_id
        else:
            # Change countryCode to "QA" for Qatar routes
            delivery_location['countryCode'] = "QA"
            
        if not self.route_id.bayan_route_from_id or not self.route_id.bayan_route_to_id:
            raise ValidationError(_("The route IDs must be set before sending a waybill request."))
        pre_format_recipient_number = self.shipping_order_id.partner_id.mobile
        recipient_formatted_mobile = self.format_mobile_number(pre_format_recipient_number)
        
        
        # Construct the rest of the data dictionary
        data = {
            "receivedDate": formatted_received_date,
            "expectedDeliveryDate": formatted_expected_delivery_date,
            "vehicle": {
                "plateTypeId": 2,
                "vehiclePlate": {
                    "rightLetter": plate_dict['rightLetter'],
                    "middleLetter": plate_dict['middleLetter'],
                    "leftLetter": plate_dict['leftLetter'],
                    "number": plate_dict['number'],
                }
            },
            "driver": {
                "identityNumber": self.driver_id.employee_iqama_number,
                "issueNumber": self.driver_id.employee_id_num_issue,
                "mobile": "+966555607720"  # Adjusted for demonstration
            },
            "waybills": [
                {
                    "deliverToClient": False,
                    "tradable": False,
                    "fare": 0,
                    "paidBySender": False,
                    "sender": {
                        "name": self.shipping_order_id.company_id.name,
                        "phone": self.shipping_order_id.company_id.phone,
                        "countryCode": "SA",
                        "cityId": self.route_id.bayan_route_from_id, 
                        "address": self.shipping_order_id.company_id.street
                    },
                    "recipient": {
                        "name": self.shipping_order_id.partner_id.name,
                        "phone": recipient_formatted_mobile, 
                        "countryCode": "SA",
                        "cityId": self.route_id.bayan_route_to_id,
                        "address": self.shipping_order_id.partner_id.street, 
                    },
                    "receivingLocation": {
                        "countryCode": "SA",
                        "cityId": self.route_id.bayan_route_from_id, 
                        "address": self.shipment_from,
                    },
                    
                    "deliveryLocation": delivery_location,
                    "items": [item],
                }
            ]
        }

        headers = {
            'Content-Type': 'application/json',
            'app_id': app_id,
            'app_key': app_key,
            'client_id': client_id,
        }
        return data, headers

    def _send_waybill_request(self, data, headers):
        url = "https://bayan.api.elm.sa/api/v1/carrier/trip"
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            response_data = response.json()
            
            # Check if 'waybills' list is not empty before accessing it
            if 'waybills' in response_data and response_data['waybills']:
                waybill_id = response_data['waybills'][0].get('waybillId')
            else:
                waybill_id = None  # Handle the case where no waybillId is returned

            self.update({
                'trip_id': response_data.get('tripId'),
                'waybill_id': waybill_id,
            })
            return None  # No error, so return None to indicate success
        else:
            # Attempt to parse the error message for more details
            try:
                error_details = response.json()  # Assume the error details are in JSON format
                # Customize this part to extract the specific error message you need
                detailed_error_msg = error_details.get('message', 'No detailed error message provided.')
                # You can also iterate through error details if they are in a list, for example
            except ValueError:
                # If response is not in JSON format, fallback to using the entire response text
                detailed_error_msg = response.text

            message = _("Failed to create trip. Status code: {}, Detailed Message: {}").format(response.status_code, detailed_error_msg)
            return self._show_message_popup(message)
    def _show_message_popup(self, message):
        message_wizard = self.env['api.message.wizard'].create({'message': message})
        return {
            'name': _('API Response'),
            'type': 'ir.actions.act_window',
            'res_model': 'api.message.wizard',
            'view_mode': 'form',
            'res_id': message_wizard.id,
            'target': 'new',
        }

    def _get_api_credentials(self):
        # These should ideally be stored securely, not hard-coded
        app_id = "5333e302"
        app_key = "e343b2ab0e63a3d2f70147bd56d15f59"
        client_id = "d88dadbb-63e8-4645-9120-df08bddb911c"
        return app_id, app_key, client_id

    def get_trip_pdf(self):
        if not self.trip_id:
            raise UserError(_("No Trip ID found for record %s.") % self.name)

        app_id, app_key, client_id = self._get_api_credentials()
        url = f"https://bayan.api.elm.sa/api/v1/carrier/trip/{self.trip_id}/print"
        headers = {
            'Content-Type': 'application/json',
            'app_id': app_id,
            'app_key': app_key,
            'client_id': client_id,
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            pdf_content_base64 = base64.b64encode(response.content).decode("utf-8")
            attachment = self.env['ir.attachment'].create({
                'name': f"Job_Num_{self.shipping_order_id.clearance_request_id.name}, Truck_{self.vehicle_id.name}, Trip_{self.trip_id}.pdf",
                'type': 'binary',
                'datas': pdf_content_base64,
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/pdf'
            })
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }
        else:
            error_msg = _("Failed to get trip PDF. Status code: {}").format(response.status_code)
            raise ValidationError(error_msg)
        
    def print_way_bill_report(self):
        self.ensure_one()
        if self.vehicle_id:
            if self.vehicle_id.driving_license_end_date:
                message = _("Driving License Expiration Date")
                self.check_date_fleet(self.vehicle_id.driving_license_end_date, message)
            if self.vehicle_id.driver_expiry_date:
                message = _("Driver Expiry Date")
                self.check_date_fleet(self.vehicle_id.driver_expiry_date, message)
            if self.vehicle_id.play_card_end_date:
                message = _("Play Card Expiration Date")
                self.check_date_fleet(self.vehicle_id.play_card_end_date, message)
            if self.vehicle_id.expiry_card_end_date:
                message = _("Expiry Card Expiration Date")
                self.check_date_fleet(self.vehicle_id.expiry_card_end_date, message)
            if self.vehicle_id.insurance_end_date:
                message = _("Insurance Expiration Date")
                self.check_date_fleet(self.vehicle_id.insurance_end_date, message)
            if self.vehicle_id.periodic_inspection_end_date:
                message = _("Periodic inspection Expiration Date")
                self.check_date_fleet(
                    self.vehicle_id.periodic_inspection_end_date, message
                )
            if self.vehicle_id.insurance_no_cargo_end_date:
                message = _("Insurance No/Cargo End Date")
                self.check_date_fleet(
                    self.vehicle_id.insurance_no_cargo_end_date, message
                )
            if self.vehicle_id.driver_license_expiry_date:
                message = _("Driver License Expiry Date")
                self.check_date_fleet(
                    self.vehicle_id.driver_license_expiry_date, message
                )
        if self.driver_id:
            driver_id = self.env["hr.employee"].search(
                [("address_home_id", "=", self.driver_id.id)], limit=1
            )
            if driver_id.insurance_end_date:
                message = _("Insurance Expiration Date")
                self.check_date_fleet(driver_id.insurance_end_date, message)
            if driver_id.driving_license_end_date:
                message = _("Driving license Expiration Date")
                self.check_date_fleet(driver_id.driving_license_end_date, message)
            if driver_id.port_licence_end_date:
                message = _("Port Licence Expiration Date")
                self.check_date_fleet(driver_id.port_licence_end_date, message)
            if driver_id.play_card_end_date:
                message = _("Drive Play Card Expiration Date")
                self.check_date_fleet(driver_id.play_card_end_date, message)
            if driver_id.health_certificate_end_date:
                message = _("Health certificate Expiration Date")
                self.check_date_fleet(driver_id.health_certificate_end_date, message)
        # confirm shipping order line
        if not self.confirmed:
            self.confirmed = True
        # create payment reward
        if not self.payment_reward_id:
            self.create_reward_payment()
            
        dammam_name_id = ['Farha Logistic Dammam', 'فرحه لوجستك الدمام']
        if self.shipping_order_id.company_id.name in dammam_name_id:
            self.print_way_bill_report_done = True
        return self.env.ref("transportation.report_way_bill_line").report_action(self)

    def print_way_bill_bayan(self):
        self.ensure_one()    
        action = self.create_waybill_bayan()
        if action:
            # If the method returned an action (e.g., a pop-up), return it to show the pop-up
            return action
        # If no action was returned, proceed to generate and show the PDF
        if self.trip_id:
            return self.get_trip_pdf()
        else:
            raise UserError(_("No Trip ID found. Cannot proceed with printing the waybill PDF."))

