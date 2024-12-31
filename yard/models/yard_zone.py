from odoo import models, fields, api, _




class YardZone(models.Model):
    _name = 'yard.zone'
    _description = 'Yard Zone'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    name = fields.Char(string='Zone Name', required=True)
    zone_size = fields.Selection([('20ft', '20FT'), ('40ft', '40FT')], required=True, string="Zone Size")
    zone_type = fields.Selection(
        [('20', '20 Feet'), ('40', '40 Feet'), ('40E', '40 Feet Empty'), ('20E', '20 Feet Empty'),
         ('20S', '20 Feet Small'), ('40S', '40 Feet Small'), ('40Mix', '40 Feet Mix'), 
         ('20Mix', '20 Feet Mix'), ('Tank1', 'ISO Tank 1'), ('Tank2', 'ISO Tank 2')],
        string='Zone Type', required=True)
    max_capacity = fields.Integer(string='Max Capacity', required=True)
    container_ids = fields.One2many('yard.container', 'zone_id', string='Containers')

    def create_zone_containers_lines(self):
        """Create lines for container_ids"""
        self.ensure_one()
        self.container_ids = [(5, 0, 0)]  # clear existing records
        container_names = self.generate_containers_names_based_on_capacity()
        vals_list = []
        for name in container_names:
            vals = {
                "zone_id": self.id,
                "name": name,
            }
            vals_list.append((0, 0, vals))
        self.container_ids = vals_list

    def generate_containers_names_based_on_capacity(self):
        names = []
        letter = 'A'
        number = 1
        for _ in range(self.max_capacity):
            names.append(f"{letter}({number})")
            number += 1
            if number > 10:
                number = 1
                letter = chr(ord(letter) + 1)
        return names

    @api.onchange('container_ids')
    def _onchange_container_ids(self):
        for zone in self:
            if zone.zone_type == '20':
                max_capacity = 160
            elif zone.zone_type == '40':
                max_capacity = 80
            elif zone.zone_type == '40E':
                max_capacity = 54
            elif zone.zone_type == '20E':
                max_capacity = 90
            elif zone.zone_type == '20S':
                max_capacity = 36
            elif zone.zone_type == '40S':
                max_capacity = 24
            elif zone.zone_type == '40Mix':
                max_capacity = 60
            elif zone.zone_type == '20Mix':
                max_capacity = 48
            elif zone.zone_type == 'Tank1':
                max_capacity = 48
            elif zone.zone_type == 'Tank2':
                max_capacity = 36
            else:
                max_capacity = 0  # Handle unknown zone types appropriately

            container_count = len(zone.container_ids)
            zone.max_capacity = max_capacity - container_count

