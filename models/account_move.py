# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_export_compta_id = fields.Many2one('is.export.compta', 'Folio', copy=False)
