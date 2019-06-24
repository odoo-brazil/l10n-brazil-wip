# -*- coding: utf-8 -*-
# Copyright 2019 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class L10nBrAccountMoveTemplateLine(models.Model):
    _name = 'l10n_br_account.move.template.line'
    _description = 'Item de partida dobrada'

    template_id = fields.Many2one(
        comodel_name='l10n_br_account.move.template',
        string=u'Modelo',
        required=True,
        ondelete='cascade',
    )
    model_ids = fields.Many2many(
        comodel_name='ir.model',
        related='template_id.model_ids',
        readonly=True,
    )
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string=u'Campo',
        required=True,
    )
    account_debit_id = fields.Many2one(
        comodel_name='account.account',
        string=u'Débito',
    )
    account_credit_id = fields.Many2one(
        comodel_name='account.account',
        string=u'Crédito',
    )

    @api.onchange('model_ids')
    def _onchange_model_ids(self):
        return {
            'domain': {
                'field_id': [
                    ('model_id', 'in', self.model_ids.ids),
                    ('ttype', 'in', ['float', 'monetary'])
                ]
            }
        }
