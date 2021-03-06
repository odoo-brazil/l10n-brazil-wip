# Copyright (C) 2019  Renato Lima - Akretion <renato.lima@akretion.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from erpbrasil.base import misc

from odoo import models

from odoo.addons.l10n_br_fiscal.constants.fiscal import MODELO_FISCAL_NFE


class NFe(models.Model):
    _name = 'l10n_br_nfe.document'
    _inherit = [
        'l10n_br_fiscal.document',
        'l10n_br_fiscal.document.electronic']
    _table = 'l10n_br_fiscal_document'
    _description = 'NFe'

    def _generate_key(self):
        key = super()._generate_key()
        if self.document_type_id.code == MODELO_FISCAL_NFE:
            # TODO Deveria estar no erpbrasil.base.fiscal
            company = self.company_id.partner_id
            chave = str(company.state_id and
                        company.state_id.ibge_code or "").zfill(2)

            chave += self.date.strftime("%y%m").zfill(4)

            chave += str(misc.punctuation_rm(
                self.company_id.partner_id.cnpj_cpf)).zfill(14)
            chave += str(self.document_type_id.code or "").zfill(2)
            chave += str(self.document_serie or "").zfill(3)
            chave += str(self.number or "").zfill(9)

            #
            # A inclusão do tipo de emissão na chave já torna a chave válida
            # também para a versão 2.00 da NF-e
            #
            chave += str(1).zfill(1)

            #
            # O código numério é um número aleatório
            #
            # chave += str(random.randint(0, 99999999)).strip().rjust(8, '0')

            #
            # Mas, por segurança, é preferível que esse número não seja
            # aleatório de todo
            #
            soma = 0
            for c in chave:
                soma += int(c) ** 3 ** 2

            codigo = str(soma)
            if len(codigo) > 8:
                codigo = codigo[-8:]
            else:
                codigo = codigo.rjust(8, "0")

            chave += codigo

            soma = 0
            m = 2
            for i in range(len(chave) - 1, -1, -1):
                c = chave[i]
                soma += int(c) * m
                m += 1
                if m > 9:
                    m = 2

            digito = 11 - (soma % 11)
            if digito > 9:
                digito = 0

            chave += str(digito)
            # FIXME: Fazer sufixo depender do modelo
            key = 'NFe' + chave

        return key
