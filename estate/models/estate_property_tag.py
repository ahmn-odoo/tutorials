from odoo import models, fields

class PropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "bla"
    _order = 'name'
    _sql_constraints = [
            ('name_uniq', 'UNIQUE(name)', 'The tag must be unique.')
        ]
    
    color = fields.Integer('Color')
    name = fields.Char('Name', required=True)