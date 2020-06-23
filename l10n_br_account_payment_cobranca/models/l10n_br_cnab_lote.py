# © 2012 KMEE INFORMATICA LTDA
#   @author  Luiz Felipe do Divino Costa <luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields, models

from ..constantes import STATE_CNAB

_logger = logging.getLogger(__name__)


class L10nBrCnabLote(models.Model):

    _name = "l10n_br.cnab.lote"

    account_bank_id = fields.Many2one(
        string="Conta Bancária", comodel_name="res.partner.bank"
    )
    cnab_id = fields.Many2one(
        string="CNAB", comodel_name="l10n_br.cnab", ondelete="cascade"
    )
    empresa_inscricao_numero = fields.Char(string="Número de Inscrição")
    empresa_inscricao_tipo = fields.Char(string="Tipo de Inscrição")
    evento_id = fields.One2many(
        string="Eventos", comodel_name="l10n_br.cnab.evento", inverse_name="lote_id"
    )
    mensagem = fields.Char(string="Mensagem")
    qtd_registros = fields.Integer(string="Quantidade de Registros")
    servico_operacao = fields.Char(string="Tipo de Operação")
    state = fields.Selection(
        string="State", related="cnab_id.state", selection=STATE_CNAB, default="draft"
    )
    tipo_servico = fields.Char(string="Tipo do Serviço")
    total_valores = fields.Float(string="Valor Total")