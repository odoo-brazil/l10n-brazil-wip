# -*- coding: utf-8 -*-
# Copyright 2018 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import tempfile

from dateutil.relativedelta import relativedelta

from mdfelib.v3_00 import mdfe as mdfe3, evEncMDFe, evCancMDFe
from mdfelib.v3_00 import procMDFe
from mdfelib.v3_00 import mdfeModalRodoviario as rodo3
from pynfe.processamento.mdfe import ComunicacaoMDFe

_logger = logging.getLogger(__name__)

try:
    from pybrasil.data import parse_datetime, data_hora_horario_brasilia
except (ImportError, IOError) as err:
    _logger.debug(err)

_logger = logging.getLogger(__name__)

from odoo import fields, models
from odoo.addons.l10n_br_base.tools.misc import punctuation_rm


class SpedDocumento(models.Model):
    _inherit = 'sped.documento'

    def _prepara_ender_emtit(self):
        ende_emi = mdfe3.TEndeEmi()
        
        ende_emi.set_xLgr(self.empresa_id.endereco)
        ende_emi.set_nro(self.empresa_id.numero)
        ende_emi.set_xBairro(self.empresa_id.bairro)
        ende_emi.set_cMun(self.empresa_id.municipio_id.codigo_ibge[:7])
        ende_emi.set_xMun(self.empresa_id.municipio_id.nome)
        ende_emi.set_CEP(punctuation_rm(self.empresa_id.cep))
        ende_emi.set_UF(self.empresa_id.estado)
        
        return ende_emi

    def _prepara_emit(self):
        emit_type = mdfe3.emitType()
        emit_type.set_CNPJ(self.empresa_id.cnpj_cpf_numero)
        emit_type.set_IE(punctuation_rm(self.empresa_id.participante_id.ie))
        emit_type.set_xNome(self.empresa_id.participante_id.razao_social)
        emit_type.set_xFant(self.empresa_id.participante_id.fantasia)
        emit_type.set_enderEmit(self._prepara_ender_emtit())

        return emit_type

    def _prepara_ide(self):

        ide_type = mdfe3.ideType()

        ide_type.set_cUF(self.empresa_id.municipio_id.estado_id.codigo_ibge)
        ide_type.set_UFIni(self.empresa_id.estado)
        ide_type.set_UFFim(self.descarregamento_estado_id.uf or self.empresa_id.estado)

        ide_type.set_tpAmb(self.ambiente_nfe)
        ide_type.set_tpEmit(self.tipo_emitente)
        ide_type.set_mod(self.modelo)
        ide_type.set_serie(self.serie)
        ide_type.set_nMDF(str(int(self.numero)))
        ide_type.set_modal(self.operacao_id.modalidade_transporte)

        ide_type.set_procEmi('0')
        ide_type.set_verProc('Odoo')

        dhIniViagem = data_hora_horario_brasilia(
            parse_datetime(self.data_hora_entrada_saida + ' GMT')
        ).strftime('%Y-%m-%dT%H:%M:%S-03:00')
        ide_type.set_dhIniViagem(dhIniViagem)
        ide_type.validate_TDateTimeUTC(ide_type.dhIniViagem)
        ide_type.set_dhEmi(data_hora_horario_brasilia(
            parse_datetime(self.data_hora_emissao + ' GMT')
        ).strftime('%Y-%m-%dT%H:%M:%S-03:00'))

        ide_type.set_infMunCarrega([mdfe3.infMunCarregaType(
            cMunCarrega=municipio.codigo_ibge[:7],
            xMunCarrega=municipio.nome)
            for municipio in self.carregamento_municipio_ids])

        ide_type.set_infPercurso([mdfe3.infPercursoType(
            UFPer=percurso.uf) for percurso in self.percurso_estado_ids])

        ide_type.set_indCanalVerde(None)
        ide_type.set_tpEmis('1')
        ide_type.set_tpTransp(self.tipo_transportador or None)

        return ide_type

    def _prepara_tot(self):
        tot_type = mdfe3.totType()
        
        tot_type.set_qCTe(None)  # todo: quantidade de CTe's de lista_cte
        tot_type.set_qNFe('1')  # todo: quantidade de NFe's de lista_nfe
        tot_type.set_qMDFe(None)
        tot_type.set_vCarga('3044.00')  # todo: soma do valor das NFe's, @mileo essses valores eles não tem nas linhas
        tot_type.set_cUnid('01')  # 01-KG, 02-TON
        tot_type.set_qCarga('57.0000')  # todo: Peso Bruto Total
        
        return tot_type

    def _prepara_modal(self):
        veiculo = rodo3.veicTracaoType()

        rodo = rodo3.rodo()
        
        veiculo.set_cInt('0001')
        veiculo.set_placa(punctuation_rm(self.veiculo_placa))
        veiculo.set_RENAVAM(None)
        veiculo.set_tara(str(int(self.veiculo_tara_kg)) or '0')
        veiculo.set_capKG(str(int(self.veiculo_capacidade_kg)) or '0')
        veiculo.set_capM3(str(int(self.veiculo_capacidade_m3)) or '0')
        veiculo.set_prop(None)
        veiculo.set_condutor(self.condutor_ids.monta_mdfe())
        veiculo.set_tpRod(self.veiculo_tipo_rodado or '')
        veiculo.set_tpCar(str(int(self.veiculo_tipo_carroceria)).zfill(2) or '00')
        veiculo.set_UF(self.veiculo_estado_id.uf or '')

        rodo.set_infANTT(None)
        rodo.set_veicTracao(veiculo)
        # rodo.set_veicReboque(None)
        rodo.set_codAgPorto(None)
        # rodo.set_lacRodo(None)

        return mdfe3.infModalType(versaoModal="3.00", anytypeobjs_=rodo)

    def _prepara_inf_doc(self):

        inf_mun_descarga = self.item_mdfe_ids.monta_mdfe()
        return mdfe3.infDocType(
            infMunDescarga=inf_mun_descarga
        )

    def modulo_11(self, valor):
        soma = 0
        m = 2
        for i in range(len(valor)-1, -1, -1):
            c = valor[i]
            soma += int(c) * m
            m += 1
            if m > 9:
                m = 2

        digito = 11 - (soma % 11)
        if digito > 9:
            digito = 0

        return digito

    def gera_chave(self, inf_mdfe):
        numero = 'nMDF'
        codigo_numerico = 'cMDF'

        chave = unicode(inf_mdfe.ide.cUF).zfill(2)
        chave += unicode(inf_mdfe.ide.dhEmi[2:7].replace('-', ''))
        chave += unicode(inf_mdfe.emit.CNPJ).zfill(14)
        chave += unicode(inf_mdfe.ide.mod).zfill(2)
        chave += unicode(inf_mdfe.ide.serie).zfill(3)
        chave += unicode(
            getattr(inf_mdfe.ide, numero)
        ).zfill(9)
        chave += unicode(inf_mdfe.ide.tpEmis).zfill(1)
        soma = 0
        for c in chave:
            soma += int(c) ** 3 ** 2

        codigo = unicode(soma)
        if len(codigo) > 8:
            codigo = codigo[-8:]
        else:
            codigo = codigo.rjust(8, '0')

        chave += codigo
        setattr(inf_mdfe.ide, codigo_numerico, codigo)
        digito = self.modulo_11(chave)
        inf_mdfe.ide.set_cDV(str(digito))
        chave += unicode(digito)

        return chave

    def monta_envio(self):
        self.ensure_one()

        inf_mdfe = procMDFe.infMDFeType()
        inf_mdfe.set_versao("3.00")
        inf_mdfe.set_ide(self._prepara_ide())
        inf_mdfe.set_emit(self._prepara_emit())
        inf_mdfe.set_infModal(self._prepara_modal())
        inf_mdfe.set_infDoc(self._prepara_inf_doc())
        inf_mdfe.set_seg(self.seguro_ids.monta_mdfe())
        inf_mdfe.set_tot(self._prepara_tot())
        inf_mdfe.set_lacres(self.lacre_ids.monta_mdfe())

        inf_mdfe.set_infAdic(None)  # Usar a função do divino
        self.chave = self.gera_chave(inf_mdfe)
        inf_mdfe.set_Id('MDFe' + self.chave)
        # autXML=None,
        
        inf_mdfe.original_tagname_ = 'infMDFe'

        envio = procMDFe.TMDFe(infMDFe=inf_mdfe)
        envio.original_tagname_ = 'MDFe'
        return envio

    def gera_mdfe(self):

        cert = self.empresa_id.certificado_id.arquivo.decode('base64')
        pw = self.empresa_id.certificado_id.senha
        uf = self.empresa_id.estado

        caminho = tempfile.gettempdir() + '/certificado.pfx'
        f = open(caminho, 'wb')
        f.write(cert)
        f.close()

        return ComunicacaoMDFe(certificado=caminho, senha=pw, uf=uf,
                               homologacao=(self.ambiente_nfe == '2'))

    def monta_encerramento(self):

        nSeqEvento = '01'
        tpEvento = '110112'

        encerramento = evEncMDFe.evEncMDFe()
        encerramento.set_descEvento('Encerramento')
        encerramento.set_nProt(self.protocolo_autorizacao)
        encerramento.set_dtEnc(fields.Date.today())
        encerramento.set_cUF(self.empresa_id.municipio_id.estado_id.codigo_ibge)
        encerramento.set_cMun(self.empresa_id.municipio_id.codigo_ibge[:7])
        
        det_evento = evEncMDFe.detEventoType(versaoEvento='3.00', 
                                             anytypeobjs_=encerramento)

        inf_evento = evEncMDFe.infEventoType()
        inf_evento.set_cOrgao(self.empresa_id.municipio_id.estado_id.codigo_ibge)
        inf_evento.set_tpAmb('2')
        inf_evento.set_CNPJ('41426966004836')
        inf_evento.set_chMDFe(self.chave)
        inf_evento.set_dhEvento((fields.Datetime.from_string(
            fields.Datetime.now()) + relativedelta(
            hours=-3)).strftime('%Y-%m-%dT%H:%M:%S-03:00'))
        inf_evento.set_tpEvento(tpEvento)
        inf_evento.set_nSeqEvento(nSeqEvento)
        inf_evento.set_detEvento(det_evento)
        inf_evento.set_Id('ID' + tpEvento + self.chave + nSeqEvento)

        return inf_evento

    def monta_cancelamento(self):

        nSeqEvento = '01'
        tpEvento = '110111'

        cancelamento = evCancMDFe.evCancMDFe()
        cancelamento.set_descEvento('Cancelamento')
        cancelamento.set_nProt(self.protocolo_autorizacao)
        cancelamento.set_xJust(self.justificativa)

        det_evento = evEncMDFe.detEventoType(versaoEvento='3.00',
                                             anytypeobjs_=cancelamento)

        inf_evento = evEncMDFe.infEventoType()
        inf_evento.set_cOrgao(self.empresa_id.municipio_id.estado_id.codigo_ibge)
        inf_evento.set_tpAmb('2')
        inf_evento.set_CNPJ('41426966004836')
        inf_evento.set_chMDFe(self.chave)
        inf_evento.set_dhEvento((fields.Datetime.from_string(
            fields.Datetime.now()) + relativedelta(
            hours=-3)).strftime('%Y-%m-%dT%H:%M:%S-03:00'))
        inf_evento.set_tpEvento(tpEvento)
        inf_evento.set_nSeqEvento(nSeqEvento)
        inf_evento.set_detEvento(det_evento)
        inf_evento.set_Id('ID' + tpEvento + self.chave + nSeqEvento)

        return inf_evento