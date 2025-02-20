from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Etiquetes'

    name = fields.Char('Nom', required=True)