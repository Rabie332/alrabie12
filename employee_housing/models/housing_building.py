import re
from datetime import datetime
from odoo import api, fields, models

import base64


class HousingBuilding(models.Model):
    _name = "housing.building"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Building Records"

    name = fields.Char(string='Building', required=True)
    city = fields.Char()
    district = fields.Char()
    national_address = fields.Text()
    responsible_id = fields.Many2one(
        "hr.employee", string="Building Responsible")
    unit_ids = fields.One2many("housing.unit", "building_id")
    number_of_units = fields.Integer(compute='_count_unit')
    occupancy = fields.Float(
        string="Occupancy Percentage", compute='_occupancy')
    max_rate = fields.Integer(string='Maximum rate', default=100)
    total_partially_full_units = fields.Integer(
        string='Partially Full Units', compute='_count_partially_full')
    total_available_units = fields.Integer(
        string='Available Units', compute='_count_available')
    total_full_units = fields.Integer(
        string='Full Units', compute='_count_full')
    location = fields.Char(string='Location', compute='_compute_location_map')
    latitude = fields.Char(string='Latitude')
    longitude = fields.Char(string='Longitude')
    attachmentss = fields.Many2many('ir.attachment', string="Attachments")
    unit_ids = fields.One2many("housing.unit", "building_id", string='Units')



    @api.depends('number_of_units', )
    def _count_full(self):
        for r in self:
            r.total_full_units = self.env['housing.unit'].search_count(
                [('building_id', '=', r.id), ('state', '=', 'full')])
            
    @api.depends('number_of_units', )
    def _count_available(self):
        for r in self:
            r.total_available_units = self.env['housing.unit'].search_count(
                [('building_id', '=', r.id), ('state', '=', 'available')])

    @api.depends('number_of_units', )
    def _count_partially_full(self):
        for r in self:
            r.total_partially_full_units = self.env['housing.unit'].search_count(
                [('building_id', '=', r.id), ('state', '=', 'partially_full')])
            
    def _compute_location_map(self):
        for record in self:
            if record.latitude and record.longitude:
                record.location = '<iframe width="100%" height="300" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://maps.google.com/maps?q={},{}&hl=es;z=14&amp;output=embed"></iframe>'.format(
                    record.latitude, record.longitude)
            else:
                record.location = ''

    def _count_unit(self):
        for r in self:
            if not len(r.unit_ids):
                r.number_of_units = 0
            else:
                r.number_of_units = len(r.unit_ids)

    @api.depends('number_of_units', 'occupancy')
    def _occupancy(self):
        for r in self:
            total_busy = self.env['housing.unit'].search_count(
                [('building_id', '=', r.id), ('state', '=', 'full')])
            if not len(r.unit_ids):
                r.occupancy = 0.0
            else:
                r.occupancy = 100 * total_busy / len(r.unit_ids)