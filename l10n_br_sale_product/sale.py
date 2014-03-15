# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2014  Renato Lima - Akretion                                  #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU Affero General Public License for more details.                          #
#                                                                             #
#You should have received a copy of the GNU Affero General Public License     #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons import decimal_precision as dp


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        result = {}
        for order in self.browse(cr, uid, ids, context=context):
            result[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'amount_extra': 0.0,
                'amount_discount': 0.0,
                'amount_gross': 0.0,
            }
            val = val1 = val2 = val3 = val4 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
                val2 += (line.insurance_value + line.freight_value + line.other_costs_value)
                val3 += line.discount_value
                val4 += line.price_gross
            result[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            result[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            result[order.id]['amount_extra'] = cur_obj.round(cr, uid, cur, val2)
            result[order.id]['amount_total'] = result[order.id]['amount_untaxed'] + result[order.id]['amount_tax'] + result[order.id]['amount_extra']
            result[order.id]['amount_discount'] = cur_obj.round(cr, uid, cur, val3)
            result[order.id]['amount_gross'] = cur_obj.round(cr, uid, cur, val4)
        return result

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(
            cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id',
                    'discount', 'product_uom_qty', 'freight_value',
                    'insurance_value', 'other_costs_value'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id',
                    'discount', 'product_uom_qty', 'freight_value',
                    'insurance_value', 'other_costs_value'], 10),
            },
              multi='sums', help="The total amount."),
        'amount_extra': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Extra',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id',
                    'discount', 'product_uom_qty', 'freight_value',
                    'insurance_value', 'other_costs_value'], 10),
            },
              multi='sums', help="The total amount."),
        'amount_discount': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Desconto (-)',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id',
                    'discount', 'product_uom_qty', 'freight_value',
                    'insurance_value', 'other_costs_value'], 10),
            },
              multi='sums', help="The discount amount."),
        'amount_gross': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Vlr. Bruto',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id',
                    'discount', 'product_uom_qty', 'freight_value',
                    'insurance_value', 'other_costs_value'], 10),
            },
              multi='sums', help="The discount amount."),
        'amount_freight': fields.float('Frete',
             digits_compute=dp.get_precision('Account'), readonly=True,
                               states={'draft': [('readonly', False)]}),
        'amount_costs': fields.float('Outros Custos',
            digits_compute=dp.get_precision('Account'), readonly=True,
                               states={'draft': [('readonly', False)]}),
        'amount_insurance': fields.float('Seguro',
            digits_compute=dp.get_precision('Account'), readonly=True,
                               states={'draft': [('readonly', False)]}),
        'discount_rate': fields.float('Desconto', readonly=True,
                               states={'draft': [('readonly', False)]}),
    }
    _defaults = {
        'amount_freight': 0.00,
        'amount_costs': 0.00,
        'amount_insurance': 0.00,
    }

    def _fiscal_comment(self, cr, uid, order, context=None):
        fp_comment = []
        fc_comment = []
        fc_ids = []

        fp_comment = super(SaleOrder, self)._fiscal_comment(
            cr, uid, order, context)

        for line in order.order_line:
            if line.product_id.ncm_id:
                fc = line.product_id.ncm_id
                if fc.inv_copy_note and fc.note:
                    if not fc.id in fc_ids:
                        fc_comment.append(fc.note)
                        fc_ids.append(fc.id)

        return fp_comment + fc_comment

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sale order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        result = super(SaleOrder, self)._prepare_invoice(
            cr, uid, order, lines, context)
        #TODO - Testar se só sobrescrevendo o metodo _fiscal_comment nao precisa fazer isso
        comment = []
        fiscal_comment = self._fiscal_comment(cr, uid, order, context=context)
        result['comment'] = " - ".join(comment + fiscal_comment)
        return result


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'
    _columns = {
        'insurance_value': fields.float('Insurance',
             digits_compute=dp.get_precision('Account')),
        'other_costs_value': fields.float('Other costs',
             digits_compute=dp.get_precision('Account')),
        'freight_value': fields.float('Freight',
             digits_compute=dp.get_precision('Account')),
    }
    _defaults = {
        'insurance_value': 0.00,
        'other_costs_value': 0.00,
        'freight_value': 0.00,
    }

    def _prepare_order_line_invoice_line(self, cr, uid, line,
                                         account_id=False, context=None):
        result = super(SaleOrderLine, self)._prepare_order_line_invoice_line(
            cr, uid, line, account_id, context)

        result['insurance_value'] = line.insurance_value
        result['other_costs_value'] = line.other_costs_value
        result['freight_value'] = line.freight_value

        if line.product_id.fiscal_type == 'product':
            cfop = self.pool.get("account.fiscal.position").read(
                cr, uid, [result['fiscal_position']], ['cfop_id'],
                context=context)
            if cfop[0]['cfop_id']:
                result['cfop_id'] = cfop[0]['cfop_id'][0]
        return result
