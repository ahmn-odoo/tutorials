from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils

class Property(models.Model):
    _name = "estate.property"
    _description = "bla"
    _order = 'id desc'
    _sql_constraints = [
        ('check_expected_price_positive', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive.'),
        ('check_selling_price_positive', 'CHECK(selling_price >= 0)', 'The expected price must be positive.')
    ]
    
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    name = fields.Char('Property Name', required=True)
    description = fields.Text('Property Description')
    postcode = fields.Char('Postcode')
    date_availability = fields.Date('Date Availability', copy=False, default=lambda self: date.today() + relativedelta(months=3))
    expected_price = fields.Float('Expected Price', required=True)
    selling_price = fields.Float('Selling Price', copy=False, compute='_compute_offer_accepted', store=True)
    bedrooms = fields.Integer('Number of Bedrooms', default=2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer('Number of Facades')
    garage = fields.Boolean('Garage?')
    garden = fields.Boolean('Garden?')
    garden_area = fields.Integer('Garden Area')
    garden_orientation = fields.Selection(string='Garden Orientation', selection=[('north', 'North'),('south', 'South'),('east', 'East'),('west', 'West')])
    state = fields.Selection(string='Status', selection=[('new', 'New'),('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('cancelled', 'Cancelled')], required=True, copy=False, default='new')
    active = fields.Boolean('Active', default=True)
    buyer = fields.Many2one('res.partner', string='Buyer', compute='_compute_offer_accepted', store=True)
    salesperson = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)
    tags_ids = fields.Many2many('estate.property.tag', string='Tags')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    total_area = fields.Integer(string='Total Area (sqm)', compute='_compute_total_area')
    best_price = fields.Float('Best Offer', compute='_compute_best_price')
    
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
            
    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped('price'), default=0.0)
            
    @api.depends('offer_ids.status')
    def _compute_offer_accepted(self):
        for record in self:
            record.selling_price = 0.0
            record.buyer = False
            for offer in record.offer_ids:
                if offer.status == 'accepted':
                    record.selling_price = offer.price
                    record.buyer = offer.partner_id
                    break
                
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False
    
    @api.constrains('selling_price', 'expected_price')
    def _check_price(self):
        for record in self:
            if (not float_utils.float_is_zero(record.selling_price, precision_rounding=0.01)) and float_utils.float_compare(record.selling_price, record.expected_price*0.9, precision_rounding=0.01) < 0:
                raise ValidationError('The selling price must be atleast 90% of the expected price.')
                
    @api.ondelete(at_uninstall=True)
    def _unlink_if_state_new_or_cancelled(self):
        if self.filtered(lambda record: record.state not in ['new', 'cancelled']):
            raise UserError('You cannot delete a property that is not new or cancelled.')
        
    def action_property_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError('Cancelled properties cannot be sold')
            else:
                record.state = 'sold'
        return True    
            
    def action_property_cancelled(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('Sold properties cannot be cancelled')
            else:
                record.state = 'cancelled'
        return True