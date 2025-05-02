from odoo import api, models, fields

class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "bla"
    _order = 'sequence, name'
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'The type must be unique.')
    ]
    
    name = fields.Char('Property Type Name', required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    sequence = fields.Integer('Sequence', default=1)
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='Offers')
    offer_count = fields.Integer(string='Offers Count', compute='_compute_offer_count')

    
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)