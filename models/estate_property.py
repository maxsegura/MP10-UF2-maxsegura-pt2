from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

# Definim el model 'EstateProperty' que representarà una propietat immobiliària
class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Model per estate_property'

    # Nom de la propietat, és un camp obligatori de text curt
    name = fields.Char('Nom', required=True)

    # Descripció de la propietat, és un text llarg
    description = fields.Text('Descripció')

    # Codi postal, és un camp obligatori de text curt
    postalcode = fields.Char('Codi Postal', required=True)

    # Data de disponibilitat, amb un valor per defecte que és un mes després de la creació
    date_availability = fields.Date(
        string="Data de Disponibilitat", 
        default=lambda self: fields.Date.today() + relativedelta(months=1), 
        copy=False
    )

    # Preu de venda esperat, valor en euros
    selling_price = fields.Float('Preu de Venda Esperat', required=True)

    # Preu de venda final, només lectura i no copiable
    final_price = fields.Float('Preu de Venda Final', readonly=True, copy=False)

    # Millor oferta, es calcula automàticament a partir de les ofertes rebudes
    best_offer = fields.Float('Millor Oferta', compute="_compute_best_offer", readonly=True, store=False)

    # Estat de la propietat amb els valors possibles: Nova, Oferta Rebuda, Oferta Acceptada, Venuda, Cancel·lada
    state = fields.Selection(
        [
            ('new', 'Nova'),
            ('offer_received', 'Oferta Rebuda'),
            ('offer_accepted', 'Oferta Acceptada'),
            ('sold', 'Venuda'),
            ('canceled', 'Cancel·lada'),
        ], 
        default='new', string="Estat"
    )

    # Nombre d'habitacions, és un camp obligatori numèric
    bedrooms = fields.Integer('Nombre d\'Habitacions', required=True)

    # Tipus de propietat, relacionat amb el model 'estate.property.type'
    type_id = fields.Many2one('estate.property.type', string="Tipus")

    # Etiquetes que poden ser definides per l'usuari dins de l'aplicació
    tag_ids = fields.Many2many('estate.property.tag', string="Etiquetes")

    # Indicador d'ascensor, valor per defecte a Fals
    has_elevator = fields.Boolean('Ascensor', default=False)

    # Indicador de parking, valor per defecte a Fals
    has_parking = fields.Boolean('Parking', default=False)

    # Indicador de renovació, valor per defecte a Fals
    is_renovated = fields.Boolean('Renovat', default=False)

    # Nombre de banys
    bathrooms = fields.Integer('Banys')

    # Superfície en m2 de la propietat, és un camp obligatori
    area = fields.Float('Superfície (m2)', required=True)

    # Preu per m2, calculat automàticament i no modificable
    price_per_m2 = fields.Float('Preu per m2', compute="_compute_price_per_m2", store=False)

    # Any de construcció de la propietat
    construction_year = fields.Integer('Any de Construcció')

    # Certificat energètic, amb valors predeterminats de A a G
    energy_certificate = fields.Selection(
        [('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E'), ('f', 'F'), ('g', 'G')], 
        string="Certificat Energètic"
    )

    # Estat de l'atribut actiu de la propietat, per defecte a Verdader
    is_active = fields.Boolean('Actiu', default=True)

    # Llistat d'ofertes associades a aquesta propietat
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Llistat d'Ofertes")

    # Comprador de la propietat, valor calculat automàticament i no emmagatzemat
    buyer_id = fields.Many2one('res.partner', string="Comprador", compute='_compute_buyer', readonly=True, store=False)

    # Comercial associat a la propietat, per defecte és l'usuari actual
    user_id = fields.Many2one('res.users', string="Comercial", default=lambda self: self.env.user)

    # Funció per calcular la millor oferta (de les ofertes acceptades)
    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            offers = record.offer_ids.filtered(lambda o: o.state != 'rejected')
            record.best_offer = max(offers.mapped('price'), default=0)

    # Funció per calcular el preu per m2
    @api.depends('selling_price', 'area')
    def _compute_price_per_m2(self):
        for record in self:
            record.price_per_m2 = record.selling_price / record.area if record.area else 0

    # Funció per calcular el comprador basat en les ofertes acceptades
    @api.depends('offer_ids.state', 'offer_ids.price')
    def _compute_buyer(self):
        for record in self:
            accepted_offer = record.offer_ids.filtered(lambda o: o.state == 'accepted')
            if accepted_offer:
                best_accepted_offer = max(accepted_offer, key=lambda o: o.price)
                record.buyer_id = best_accepted_offer.buyer_id
                record.final_price = best_accepted_offer.price
            else:
                record.buyer_id = False
                record.final_price = 0