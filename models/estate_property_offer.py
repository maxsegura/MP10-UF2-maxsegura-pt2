from odoo import models, fields

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Ofertes'

    # Detalls de l'oferta
    price = fields.Float('Preu Oferit', required=True)
    state = fields.Selection(
        [
            ('accepted', 'Acceptada'),
            ('rejected', 'Rebutjada'),
            ('pending', 'En tractament')
        ], 
        default='pending', string="Estat"
    )
    buyer_id = fields.Many2one('res.partner', string="Comprador")
    comments = fields.Text('Comentaris')
    property_id = fields.Many2one('estate.property', string="Propietat", readonly=True)

    # Mètode per acceptar l'oferta
    def action_accept(self):
        self.ensure_one()
        self.state = 'accepted'
        self.property_id.final_price = self.price
        self.property_id.buyer_id = self.buyer_id
        self.property_id.state = 'offer_accepted'

    # Mètode per rebutjar l'oferta
    def action_reject(self):
        self.ensure_one()
        self.state = 'rejected'
        
        # Comprovar si hi ha una altra oferta acceptada
        other_accepted_offer = self.property_id.offer_ids.filtered(lambda o: o.state == 'accepted' and o.id != self.id)
        
        # Actualitzar el preu i comprador de la propietat si escau
        if self.property_id.final_price == self.price:
            if other_accepted_offer:
                self.property_id.final_price = other_accepted_offer[0].price
                self.property_id.buyer_id = other_accepted_offer[0].buyer_id
            else:
                self.property_id.final_price = 0
                self.property_id.buyer_id = False
                self.property_id.state = 'new'