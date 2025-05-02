from odoo import models, fields, api

class EstateUser(models.Model):
    _inherit = 'res.users'
    _description = "bla"
    
    property_ids = fields.One2many('estate.property', 'salesperson', domain=['|', ('state','=','new'), ('state','=','offer_received')])