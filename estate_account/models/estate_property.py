from odoo import models, Command

class EstateProperty(models.Model):
    _inherit = 'estate.property'
    _description = "bla"
    
    def action_property_sold(self):
        for record in self:   
            self.env['account.move'].create({
                'partner_id': record.buyer.id,
                'move_type': 'out_invoice',
                'journal_id': self.env['account.journal'].search([('type', '=', 'sale')], limit=1).id,
                'line_ids': [
                    Command.create({
                        'name': record.name,
                        'quantity': 1,
                        'price_unit': record.selling_price * 0.06
                    }),
                    Command.create({
                        'name': 'Administrative Fees',
                        'quantity': 1,
                        'price_unit': 100.0
                    })
                ]
            })
        
        return super().action_property_sold()