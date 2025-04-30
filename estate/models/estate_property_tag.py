from odoo import models, fields

class property_tag(models.Model):
    _name = "estate.property.tag"
    _description = "bla"
    _order = 'name'
    color = fields.Integer('Color')
    name = fields.Char('Name', required=True)
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'The tag must be unique.')
    ]