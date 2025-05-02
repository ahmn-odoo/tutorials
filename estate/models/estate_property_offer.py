from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import float_utils

class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "bla"
    _order = 'price desc'
    _sql_constraints = [
        ('check_price_positive', 'CHECK(price > 0)', 'The price must be strictly positive.')
    ]
    
    price = fields.Float('Price')
    status = fields.Selection(string='Status', selection=[('accepted', 'Accepted'),('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one('res.partner', string='Buyer', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    validity = fields.Integer('Validity (days)', default=7)
    deadline_date = fields.Date('Deadline', compute='_compute_deadline_date', inverse='_inverse_deadline_date', default=lambda self: date.today() + relativedelta(days=7))
    property_type_id = fields.Many2one(related='property_id.property_type_id', string='Property Type', store=True)
    
    @api.depends('validity')
    def _compute_deadline_date(self):
        for record in self:
            if record.create_date:
                record.deadline_date = record.create_date + relativedelta(days=record.validity)
            else:
                record.deadline_date = False
                
    def _inverse_deadline_date(self):
        for record in self:
            if record.deadline_date and record.create_date:
                record.validity = (record.deadline_date - record.create_date.date()).days
            else:
                record.validity = 0
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            best_price = self.search([('property_id', '=', vals.get('property_id'))], limit=1).price
            if float_utils.float_compare(vals.get('price'), best_price, precision_digits=2) <= 0:
                raise UserError('The offer price must be higher than the best offer price')
            self.env['estate.property'].browse(vals.get('property_id')).state = 'offer_received'
        return super().create(vals_list)
    
    def action_accept_offer(self):
        for record in self:
            if record.status == 'refused':
                raise UserError('You cannot accept a refused offer')
            if record.property_id.offer_ids.filtered(lambda o: o.status == 'accepted'):
                raise UserError('Only one offer can be accepted for a property')
            record.status = 'accepted'
            record.property_id.state = 'offer_accepted'
        return True
            
    def action_refuse_offer(self):
        for record in self:
            if record.status == 'accepted':
                raise UserError('You cannot refuse an accepted offer')
            else:
                record.status = 'refused'
        return True
