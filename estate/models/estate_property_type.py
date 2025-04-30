from odoo import models, fields

class property_type(models.Model):
    _name = "estate.property.type"
    _description = "bla"
    _order = 'sequence, name'
    name = fields.Char('Property Type Name', required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    sequence = fields.Integer('Sequence', default=1)
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'The type must be unique.')
    ]