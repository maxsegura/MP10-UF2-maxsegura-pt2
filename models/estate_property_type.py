from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Tipus'

    name = fields.Char('Nom', required=True)