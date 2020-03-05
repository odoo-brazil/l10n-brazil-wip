# Copyright (C) 2019  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class TaxDefinitionICMS(models.Model):
    _inherit = "l10n_br_fiscal.tax.definition"

    icms_regulation_id = fields.Many2one(
        comodel_name="l10n_br_fiscal.icms.regulation",
        string="ICMS Regulation")

    state_from_id = fields.Many2one(
        comodel_name='res.country.state',
        string='From State',
        domain=[('country_id.code', '=', 'BR')])

    state_to_id = fields.Many2one(
        comodel_name='res.country.state',
        string='To State',
        domain=[('country_id.code', '=', 'BR')])

    #
    # icms_ids = fields.One2many(
    #    comodel_name="l10n_br_fiscal.tax.icms",
    #    inverse_name="regulation_id")

    # icms_st_ids = fields.One2many(
    #    comodel_name="l10n_br_fiscal.tax.icms",
    #    inverse_name="regulation_id")

    # icms_fcp_id = fields.One2many(
    #    comodel_name="l10n_br_fiscal.tax.icms",
    #    inverse_name="regulation_id")

    # name = fields.Text(string="Name", required=True, index=True)

    # icms_tax_id = fields.Many2one(
    #    comodel_name="l10n_br_fiscal.tax",
    #    string="ICMS Tax",
    #    domain="[('tax_domain', '=', 'icms')]",
    # )

    # ncms = fields.Char(string="NCM")
    #
    # ncm_exception = fields.Char(string="NCM Exeption")
    #
    # not_in_ncms = fields.Char(string="Not in NCM")
    #
    # ncm_ids = fields.Many2many(
    #     comodel_name="l10n_br_fiscal.ncm",
    #     relation="fiscal_pis_cofins_ncm_rel",
    #     colunm1="piscofins_id",
    #     colunm2="ncm_id",
    #     compute="_compute_ncms",
    #     store=True,
    #     readonly=True,
    #     string="NCMs",
    # )
    #
    # @api.depends("ncms")
    # def _compute_ncms(self):
    #     ncm = self.env["l10n_br_fiscal.ncm"]
    #     domain = False
    #     for r in self:
    #         # Clear Field
    #         domain = False
    #         r.ncm_ids = False
    #         if r.ncms:
    #             ncms = r.ncms.split(";")
    #             domain = ["|"] * (len(ncms) - 1)
    #             domain += [("code_unmasked", "=", n) for n in ncms if len(n) == 8]
    #             domain += [
    #                 ("code_unmasked", "=ilike", n + "%") for n in ncms if len(n) < 8
    #             ]
    #
    #         if r.not_in_ncms:
    #             not_in_ncms = r.not_in_ncms.split(";")
    #             domain += [
    #                 ("code_unmasked", "=", n) for n in not_in_ncms if len(n) == 8
    #             ]
    #
    #             domain += [
    #                 ("code_unmasked", "not ilike", n + "%")
    #                 for n in not_in_ncms
    #                 if len(n) < 8
    #             ]
    #
    #         if r.ncm_exception:
    #             ncm_exception = r.ncm_exception.split(";")
    #             domain += [("exception", "=", n) for n in ncm_exception]
    #
    #         if domain:
    #             r.ncm_ids = ncm.search(domain)