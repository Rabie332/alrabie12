# Corrected Python file it_tickets.py

from odoo import models, fields


class ITTicketStage(models.Model):
    _name = 'it.ticket.stage'
    _description = 'IT Ticket Stage'
    _order = 'sequence'

    name = fields.Char("Stage Name", required=True)
    sequence = fields.Integer("Sequence", default=0,
                              help="Used to order the stages.")
